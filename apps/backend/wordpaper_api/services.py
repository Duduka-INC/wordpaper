from datetime import datetime, timezone
import secrets
import string
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from wordpaper_core import AspectRatio, ResolutionPreset

from wordpaper_api.generation import generate_specs
from wordpaper_api.models import RenderRecord, WallProject, WallVersion
from wordpaper_api.rendering import encode_spec, preview_size
from wordpaper_api.schemas import (
    CreateRenderRequest,
    GenerationRequest,
    RenderOut,
    WallOut,
    WallpaperSpec,
)
from wordpaper_api.storage import LocalObjectStorage


WALL_ID_ALPHABET = string.ascii_uppercase + string.digits


def make_wall_id(db: Session) -> str:
    for _ in range(10):
        candidate = "WP-" + "".join(
            secrets.choice(WALL_ID_ALPHABET) for _ in range(8)
        )
        exists = db.scalar(
            select(func.count()).select_from(WallProject).where(
                WallProject.wall_id == candidate
            )
        )
        if not exists:
            return candidate
    raise RuntimeError("Could not allocate a wall id")


def create_version(db: Session, project: WallProject, spec: WallpaperSpec) -> WallVersion:
    version_number = len(project.versions) + 1
    version = WallVersion(
        project=project,
        version_number=version_number,
        spec=spec.model_dump(mode="json"),
        schema_version=spec.schema_version,
        renderer_version="0.1.0",
        seed=spec.seed,
        recipe_id=spec.recipe_id,
    )
    db.add(version)
    db.flush()
    return version


def create_project(
    db: Session,
    owner_session_id: str,
    spec: WallpaperSpec,
    visibility: str,
) -> WallProject:
    now = datetime.now(timezone.utc)
    project = WallProject(
        wall_id=make_wall_id(db),
        owner_session_id=owner_session_id,
        visibility=visibility,
        draft_spec=spec.model_dump(mode="json"),
        published_at=now if visibility == "public" else None,
    )
    db.add(project)
    db.flush()
    create_version(db, project, spec)
    return project


def resolve_size(spec: WallpaperSpec, request: CreateRenderRequest) -> tuple[int, int]:
    if request.resolution == "custom":
        assert request.width is not None and request.height is not None
        return request.width, request.height
    preset = ResolutionPreset(request.resolution)
    size = preset.resolve(
        AspectRatio(spec.aspect_ratio.width, spec.aspect_ratio.height)
    )
    return size.width, size.height


def render_version(
    db: Session,
    storage: LocalObjectStorage,
    version: WallVersion,
    width: int,
    height: int,
    image_format: str,
    quality: int,
    kind: str,
) -> RenderRecord:
    record = RenderRecord(
        version_id=version.id,
        kind=kind,
        width=width,
        height=height,
        format=image_format,
        quality=quality,
        status="rendering",
        started_at=datetime.now(timezone.utc),
    )
    db.add(record)
    db.flush()

    try:
        spec = WallpaperSpec.model_validate(version.spec)
        data, content_type, checksum = encode_spec(
            spec,
            width=width,
            height=height,
            image_format=image_format,
            quality=quality,
        )
        extension = "jpg" if image_format == "jpeg" else image_format
        key = f"renders/{version.project_id}/{record.id}.{extension}"
        storage.put(key, data)
        record.storage_key = key
        record.content_type = content_type
        record.byte_size = len(data)
        record.checksum = checksum
        record.status = "ready"
        record.finished_at = datetime.now(timezone.utc)
    except Exception:
        record.status = "failed"
        record.error_code = "render_failed"
        record.finished_at = datetime.now(timezone.utc)
        db.flush()
        raise

    db.flush()
    return record


def render_preview(
    db: Session,
    storage: LocalObjectStorage,
    project: WallProject,
    version: WallVersion,
) -> RenderRecord:
    spec = WallpaperSpec.model_validate(version.spec)
    width, height = preview_size(spec)
    record = render_version(
        db,
        storage,
        version,
        width,
        height,
        image_format="webp",
        quality=88,
        kind="preview",
    )
    project.cover_render_id = record.id
    db.flush()
    return record


def render_out(record: RenderRecord, storage: LocalObjectStorage) -> RenderOut:
    url = storage.public_url(record.storage_key) if record.storage_key else None
    return RenderOut(
        id=record.id,
        kind=record.kind,
        width=record.width,
        height=record.height,
        format=record.format,
        status=record.status,
        url=url,
        download_url=f"/api/v1/renders/{record.id}/download" if url else None,
        byte_size=record.byte_size,
        created_at=record.created_at,
    )


def project_out(
    db: Session,
    project: WallProject,
    storage: LocalObjectStorage,
    session_id: str | None,
) -> WallOut:
    renders = list(
        db.scalars(
            select(RenderRecord)
            .join(WallVersion)
            .where(WallVersion.project_id == project.id)
            .order_by(RenderRecord.created_at.desc())
        )
    )
    cover = next((item for item in renders if item.id == project.cover_render_id), None)
    return WallOut(
        wall_id=project.wall_id,
        visibility=project.visibility,
        revision=project.draft_revision,
        is_owner=project.owner_session_id == session_id,
        spec=WallpaperSpec.model_validate(project.draft_spec),
        cover_url=(
            storage.public_url(cover.storage_key)
            if cover is not None and cover.storage_key
            else None
        ),
        export_count=project.export_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
        renders=[render_out(record, storage) for record in renders],
    )


def seed_gallery(db: Session, storage: LocalObjectStorage, owner_session_id: str) -> None:
    count = db.scalar(select(func.count()).select_from(WallProject)) or 0
    if count:
        return

    seed_content = {
        "editorial_dictionary": (
            "consistency",
            "the ability to repeat a process with the same quality, over and over again.",
            "[kənˈsɪstənsi]",
        ),
        "liquid_sky": (
            "lucid",
            "bright, clear and easy to understand; filled with light.",
            "[ˈluːsɪd]",
        ),
        "quiet_minimal": (
            "stillness",
            "a quiet condition without movement or sound.",
            "[ˈstɪlnəs]",
        ),
        "brutalist_type": (
            "voltage",
            "electric potential expressed in volts.",
            "[ˈvəʊltɪdʒ]",
        ),
        "soft_pop": (
            "bloom",
            "to become radiant, open and full of colour.",
            "[bluːm]",
        ),
        "gothic_archive": (
            "zeitgeist",
            "the defining spirit or mood of a particular period.",
            "[ˈtsaɪtɡaɪst]",
        ),
    }

    from wordpaper_api.schemas import ContentSpec

    for index, (recipe_id, values) in enumerate(seed_content.items()):
        word, definition, transcription = values
        request = GenerationRequest(
            content=ContentSpec(
                word=word,
                definition=definition,
                transcription=transcription,
                part_of_speech="noun",
                language="English",
            ),
            recipe_id=recipe_id,
            theme="auto",
            count=1,
            seed=20260810 + index,
        )
        _, specs = generate_specs(request)
        project = create_project(
            db,
            owner_session_id,
            specs[0],
            visibility="public",
        )
        version = project.versions[-1]
        render_preview(db, storage, project, version)
        project.export_count = (index * 7 + 3) % 31
        db.commit()
