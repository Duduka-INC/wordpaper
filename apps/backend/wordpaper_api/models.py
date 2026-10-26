from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from wordpaper_api.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def uuid_string() -> str:
    return str(uuid4())


class BrowserSession(Base):
    __tablename__ = "browser_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class WallProject(Base):
    __tablename__ = "wall_projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    wall_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    owner_session_id: Mapped[str] = mapped_column(
        ForeignKey("browser_sessions.id"),
        index=True,
    )
    visibility: Mapped[str] = mapped_column(String(16), default="unlisted", index=True)
    draft_spec: Mapped[dict[str, Any]] = mapped_column(JSON)
    draft_revision: Mapped[int] = mapped_column(Integer, default=1)
    cover_render_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    export_count: Mapped[int] = mapped_column(Integer, default=0, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    versions: Mapped[list["WallVersion"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class WallVersion(Base):
    __tablename__ = "wall_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    project_id: Mapped[str] = mapped_column(ForeignKey("wall_projects.id"), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    spec: Mapped[dict[str, Any]] = mapped_column(JSON)
    schema_version: Mapped[int] = mapped_column(Integer, default=1)
    renderer_version: Mapped[str] = mapped_column(String(32), default="0.1.0")
    seed: Mapped[int] = mapped_column(BigInteger)
    recipe_id: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    project: Mapped[WallProject] = relationship(back_populates="versions")
    renders: Mapped[list["RenderRecord"]] = relationship(
        back_populates="version",
        cascade="all, delete-orphan",
    )


class RenderRecord(Base):
    __tablename__ = "renders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    version_id: Mapped[str] = mapped_column(ForeignKey("wall_versions.id"), index=True)
    kind: Mapped[str] = mapped_column(String(16), default="export")
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    format: Mapped[str] = mapped_column(String(8))
    quality: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="queued", index=True)
    storage_key: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)
    content_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    byte_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    version: Mapped[WallVersion] = relationship(back_populates="renders")


class DownloadEvent(Base):
    __tablename__ = "download_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_string)
    project_id: Mapped[str] = mapped_column(ForeignKey("wall_projects.id"), index=True)
    render_id: Mapped[str] = mapped_column(ForeignKey("renders.id"), index=True)
    session_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    format: Mapped[str] = mapped_column(String(8))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
