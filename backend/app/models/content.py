"""Scans, analysis cache, chat, marketplace and media models."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.core.timeutil import UTCDateTime, utcnow


class MediaFile(Base):
    """A sanitised image stored on disk under VAR_DIR/media/<id>.jpg."""

    __tablename__ = "media_files"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    kind: Mapped[str] = mapped_column(String(16), default="image")  # scan | chat | listing
    width: Mapped[int] = mapped_column(Integer, default=0)
    height: Mapped[int] = mapped_column(Integer, default=0)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)


class AnalysisCache(Base):
    """SHA-256 dedup cache (image + user + question + language), as in the original app."""

    __tablename__ = "analysis_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    image_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    user_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    result: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    media_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    image_hash: Mapped[str] = mapped_column(String(64), index=True)
    filename: Mapped[str | None] = mapped_column(String(160), nullable=True)
    disease: Mapped[str] = mapped_column(String(32))
    confidence: Mapped[float] = mapped_column(Float)
    is_healthy: Mapped[bool] = mapped_column(Boolean, default=False)
    distribution: Mapped[dict] = mapped_column(JSON, default=dict)
    env_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    advisory: Mapped[str] = mapped_column(Text, default="")
    sources: Mapped[list | None] = mapped_column(JSON, nullable=True)
    citations: Mapped[list | None] = mapped_column(JSON, nullable=True)
    safety_audit: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    reasons: Mapped[list | None] = mapped_column(JSON, nullable=True)
    is_blended: Mapped[bool] = mapped_column(Boolean, default=False)
    question: Mapped[str | None] = mapped_column(String(500), nullable=True)
    language: Mapped[str] = mapped_column(String(2), default="en")
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, index=True)


class ChatThread(Base):
    __tablename__ = "chat_threads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)

    messages: Mapped[list[ChatMessage]] = relationship(
        back_populates="thread", cascade="all, delete-orphan", order_by="ChatMessage.id"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    thread_id: Mapped[str] = mapped_column(ForeignKey("chat_threads.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(16))  # user | assistant
    content: Mapped[str] = mapped_column(Text)
    attached_image_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    media_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    disease: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)

    thread: Mapped[ChatThread] = relationship(back_populates="messages")


class CropListing(Base):
    __tablename__ = "crop_listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(150))
    variety: Mapped[str] = mapped_column(String(100))
    quantity: Mapped[float] = mapped_column(Float)
    quantity_unit: Mapped[str] = mapped_column(String(50), default="kg")
    quantity_kg: Mapped[float] = mapped_column(Float, index=True)
    price: Mapped[float] = mapped_column(Float)
    price_unit: Mapped[str] = mapped_column(String(80), default="per kg")
    price_per_kg: Mapped[float] = mapped_column(Float, index=True)
    farmer_name: Mapped[str] = mapped_column(String(120))
    phone_number: Mapped[str] = mapped_column(String(10))
    address: Mapped[str] = mapped_column(String(300))
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    photos: Mapped[list] = mapped_column(JSON, default=list)  # [{"media_id": "...", "caption": "..."}]
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)


class ListingReport(Base):
    __tablename__ = "listing_reports"
    __table_args__ = (UniqueConstraint("listing_id", "reported_by_user_id", name="uq_report_once"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("crop_listings.id", ondelete="CASCADE"), index=True)
    reported_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    reason: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), default=utcnow)
