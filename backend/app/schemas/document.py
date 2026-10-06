from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    original_filename: str = Field(min_length=1, max_length=500)
    content_type: str = Field(min_length=1, max_length=255)
    file_size_bytes: int | None = Field(default=None, ge=0)
    sha256: str | None = Field(default=None, min_length=64, max_length=64)
    storage_key: str | None = Field(default=None, max_length=1000)
    page_count: int | None = Field(default=None, ge=0)


class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    status: str | None = None
    error_message: str | None = None


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    title: str
    original_filename: str
    content_type: str
    file_size_bytes: int | None
    sha256: str | None
    storage_key: str | None
    page_count: int | None
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    processed_at: datetime | None
