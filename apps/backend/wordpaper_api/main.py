from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import secrets
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from sqlalchemy.orm import Session

from wordpaper_core import AnchorPosition

from wordpaper_api.config import settings
from wordpaper_api.database import Base, SessionLocal, engine, get_db
from wordpaper_api.generation import generate_specs, recipe_options
from wordpaper_api.models import (
    BrowserSession,
    DownloadEvent,
    RenderRecord,
    WallProject,
    WallVersion,
)
from wordpaper_api.rendering import encode_spec, library_resources_root, preview_size
from wordpaper_api.schemas import (
    CreateRenderRequest,
    CreateWallRequest,
    GalleryItem,
    GalleryResponse,
    GeneratedVariant,
    GenerationRequest,
    GenerationResponse,
    MetaOption,
    MetaResponse,
    UpdateWallRequest,
    WallOut,
    WallpaperSpec,
)
from wordpaper_api.services import (
    create_project,
    create_version,
    project_out,
    render_out,
    render_preview,
    render_version,
    resolve_size,
    seed_gallery,
)
from wordpaper_api.storage import LocalObjectStorage


storage = LocalObjectStorage(settings.storage_root)


def ensure_system_session(db: Session) -> BrowserSession:
    session = db.get(BrowserSession, "00000000-0000-0000-0000-000000000001")
    if session is None:
        session = BrowserSession(
            id="00000000-0000-0000-0000-000000000001",
            token_hash="system",
            expires_at=datetime.now(timezone.utc) + timedelta(days=3650),
        )
        db.add(session)
        db.commit()
    return session


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.storage_root.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        system = ensure_system_session(db)
        seed_gallery(db, storage, system.id)
    yield


app = FastAPI(
    title="Wordpaper API",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/media", StaticFiles(directory=settings.storage_root), name="media")
app.mount(
    "/library-assets",
    StaticFiles(directory=library_resources_root()),
    name="library-assets",
)


def get_browser_session(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> BrowserSession:
    token = request.cookies.get("wordpaper_session")
    if token:
        token_hash = sha256(token.encode()).hexdigest()
        existing = db.scalar(
            select(BrowserSession).where(BrowserSession.token_hash == token_hash)
        )
        if existing is not None:
            return existing

    token = secrets.token_urlsafe(32)
    browser_session = BrowserSession(
        id=str(uuid4()),
        token_hash=sha256(token.encode()).hexdigest(),
        expires_at=datetime.now(timezone.utc) + timedelta(days=365),
    )
    db.add(browser_session)
    db.commit()
    response.set_cookie(
        "wordpaper_session",
        token,
        max_age=365 * 24 * 60 * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )
    return browser_session


def require_owner(project: WallProject, session: BrowserSession) -> None:
    if project.owner_session_id != session.id:
        raise HTTPException(status_code=403, detail="Only the owner can modify this wall")


def find_project(db: Session, wall_id: str) -> WallProject:
    project = db.scalar(select(WallProject).where(WallProject.wall_id == wall_id.upper()))
    if project is None:
        raise HTTPException(status_code=404, detail="Wall not found")
    return project


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "renderer": "wordpaper-core/0.1.0"}


@app.get("/api/v1/meta", response_model=MetaResponse)
def meta() -> MetaResponse:
    fonts = (
        ("playfair_display", "Playfair Display"),
        ("newsreader", "Newsreader"),
        ("unifraktur_cook", "Unifraktur Cook"),
        ("shrikhand", "Shrikhand"),
        ("modak", "Modak"),
        ("metal_mania", "Metal Mania"),
        ("orbitron", "Orbitron"),
    )
    textures = (
        ("sky.clouds.soft", "Soft clouds"),
        ("sky.clouds.fluffy", "Fluffy clouds"),
        ("sky.clouds.sparse", "Sparse clouds"),
        ("leather.black", "Black leather"),
        ("leather.crocodile", "Crocodile leather"),
        ("fur.white", "White fur"),
        ("fur.tiger", "Tiger fur"),
        ("nature.grass", "Grass"),
        ("studio.liquid_chrome", "Liquid chrome"),
        ("studio.holographic_film", "Holographic film"),
        ("studio.risograph_grain", "Risograph grain"),
    )
    return MetaResponse(
        fonts=[MetaOption(id=id_, label=label) for id_, label in fonts],
        textures=[MetaOption(id=id_, label=label) for id_, label in textures],
        recipes=[MetaOption(id=id_, label=label) for id_, label in recipe_options()],
        anchors=[
            MetaOption(id=position.value, label=position.value.replace("_", " ").title())
            for position in AnchorPosition
        ],
        resolutions=[
            MetaOption(id="1080p", label="Full HD"),
            MetaOption(id="2k", label="2K"),
            MetaOption(id="4k", label="4K"),
            MetaOption(id="8k", label="8K"),
        ],
    )


@app.post("/api/v1/generations", response_model=GenerationResponse)
def generate(request: GenerationRequest) -> GenerationResponse:
    try:
        root_seed, specs = generate_specs(request)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    variants: list[GeneratedVariant] = []
    for spec in specs:
        width, height = preview_size(spec)
        data, _, _ = encode_spec(spec, width, height, "webp", 86)
        variant_id = str(uuid4())
        key = f"previews/{variant_id}.webp"
        storage.put(key, data)
        variants.append(
            GeneratedVariant(
                variant_id=variant_id,
                spec=spec,
                preview_url=storage.public_url(key),
            )
        )
    return GenerationResponse(seed=root_seed, variants=variants)


@app.post("/api/v1/previews", response_model=GeneratedVariant)
def preview(spec: WallpaperSpec) -> GeneratedVariant:
    width, height = preview_size(spec)
    data, _, _ = encode_spec(spec, width, height, "webp", 86)
    variant_id = str(uuid4())
    key = f"previews/{variant_id}.webp"
    storage.put(key, data)
    return GeneratedVariant(
        variant_id=variant_id,
        spec=spec,
        preview_url=storage.public_url(key),
    )


@app.post("/api/v1/walls", response_model=WallOut, status_code=201)
def create_wall(
    request: CreateWallRequest,
    db: Session = Depends(get_db),
    browser_session: BrowserSession = Depends(get_browser_session),
) -> WallOut:
    project = create_project(
        db,
        browser_session.id,
        request.spec,
        request.visibility,
    )
    render_preview(db, storage, project, project.versions[-1])
    db.commit()
    return project_out(db, project, storage, browser_session.id)


@app.get("/api/v1/gallery", response_model=GalleryResponse)
def gallery(
    sort: str = Query(default="new", pattern="^(new|popular)$"),
    theme: str | None = Query(default=None, pattern="^(light|dark)$"),
    has_text: bool | None = None,
    q: str | None = None,
    cursor: int = Query(default=0, ge=0),
    limit: int = Query(default=12, ge=1, le=40),
    db: Session = Depends(get_db),
) -> GalleryResponse:
    projects = list(
        db.scalars(select(WallProject).where(WallProject.visibility == "public"))
    )
    if q:
        needle = q.strip().upper().split("/")[-1]
        projects = [project for project in projects if needle in project.wall_id]
    if theme:
        projects = [
            project for project in projects if project.draft_spec.get("theme") == theme
        ]
    if has_text is not None:
        projects = [
            project
            for project in projects
            if bool(project.draft_spec.get("content", {}).get("word")) is has_text
        ]

    key = (
        (lambda item: item.export_count)
        if sort == "popular"
        else (lambda item: item.created_at)
    )
    projects.sort(key=key, reverse=True)
    page = projects[cursor : cursor + limit]
    items: list[GalleryItem] = []
    for project in page:
        if project.cover_render_id is None:
            continue
        cover = db.get(RenderRecord, project.cover_render_id)
        if cover is None or cover.storage_key is None:
            continue
        spec = WallpaperSpec.model_validate(project.draft_spec)
        items.append(
            GalleryItem(
                wall_id=project.wall_id,
                theme=spec.theme,
                word=spec.content.word,
                recipe_id=spec.recipe_id,
                cover_url=storage.public_url(cover.storage_key),
                aspect_ratio=spec.aspect_ratio,
                export_count=project.export_count,
            )
        )
    next_cursor = cursor + limit if cursor + limit < len(projects) else None
    return GalleryResponse(
        items=items,
        next_cursor=str(next_cursor) if next_cursor is not None else None,
    )


@app.get("/api/v1/walls/{wall_id}", response_model=WallOut)
def get_wall(
    wall_id: str,
    db: Session = Depends(get_db),
    browser_session: BrowserSession = Depends(get_browser_session),
) -> WallOut:
    project = find_project(db, wall_id)
    if project.visibility == "private" and project.owner_session_id != browser_session.id:
        raise HTTPException(status_code=404, detail="Wall not found")
    return project_out(db, project, storage, browser_session.id)


@app.patch("/api/v1/walls/{wall_id}", response_model=WallOut)
def update_wall(
    wall_id: str,
    request: UpdateWallRequest,
    db: Session = Depends(get_db),
    browser_session: BrowserSession = Depends(get_browser_session),
) -> WallOut:
    project = find_project(db, wall_id)
    require_owner(project, browser_session)
    if project.draft_revision != request.expected_revision:
        raise HTTPException(status_code=409, detail="Draft revision conflict")
    project.draft_spec = request.spec.model_dump(mode="json")
    project.draft_revision += 1
    version = create_version(db, project, request.spec)
    render_preview(db, storage, project, version)
    db.commit()
    return project_out(db, project, storage, browser_session.id)


@app.post("/api/v1/walls/{wall_id}/renders", response_model=WallOut)
def create_render(
    wall_id: str,
    request: CreateRenderRequest,
    db: Session = Depends(get_db),
    browser_session: BrowserSession = Depends(get_browser_session),
) -> WallOut:
    project = find_project(db, wall_id)
    if project.visibility == "private":
        require_owner(project, browser_session)
    spec = WallpaperSpec.model_validate(project.draft_spec)
    version = create_version(db, project, spec)
    width, height = resolve_size(spec, request)
    render_version(
        db,
        storage,
        version,
        width,
        height,
        request.format,
        request.quality,
        kind="export",
    )
    db.commit()
    return project_out(db, project, storage, browser_session.id)


@app.post("/api/v1/walls/{wall_id}/fork", response_model=WallOut, status_code=201)
def fork_wall(
    wall_id: str,
    db: Session = Depends(get_db),
    browser_session: BrowserSession = Depends(get_browser_session),
) -> WallOut:
    source = find_project(db, wall_id)
    spec = WallpaperSpec.model_validate(source.draft_spec)
    project = create_project(db, browser_session.id, spec, "unlisted")
    render_preview(db, storage, project, project.versions[-1])
    db.commit()
    return project_out(db, project, storage, browser_session.id)


@app.post("/api/v1/walls/{wall_id}/publish", response_model=WallOut)
def publish_wall(
    wall_id: str,
    db: Session = Depends(get_db),
    browser_session: BrowserSession = Depends(get_browser_session),
) -> WallOut:
    project = find_project(db, wall_id)
    require_owner(project, browser_session)
    project.visibility = "public"
    project.published_at = datetime.now(timezone.utc)
    db.commit()
    return project_out(db, project, storage, browser_session.id)


@app.get("/api/v1/renders/{render_id}/download")
def download_render(
    render_id: str,
    db: Session = Depends(get_db),
) -> FileResponse:
    record = db.get(RenderRecord, render_id)
    if record is None or record.storage_key is None or record.status != "ready":
        raise HTTPException(status_code=404, detail="Render not found")
    project = db.scalar(
        select(WallProject).join(WallVersion).where(WallVersion.id == record.version_id)
    )
    assert project is not None
    project.export_count += 1
    db.add(
        DownloadEvent(
            project_id=project.id,
            render_id=record.id,
            format=record.format,
        )
    )
    db.commit()
    path = storage.resolve(record.storage_key)
    return FileResponse(
        path,
        media_type=record.content_type,
        filename=f"{project.wall_id}.{path.suffix.lstrip('.')}",
    )
