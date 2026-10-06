from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.document import Document
from backend.app.schemas.document import DocumentCreate, DocumentUpdate
from backend.app.services.state_machine import transition_status


def create_document(
    db: Session,
    owner_id: UUID,
    data: DocumentCreate,
) -> Document:
    document = Document(
        owner_id=owner_id,
        title=data.title,
        original_filename=data.original_filename,
        content_type=data.content_type,
        file_size_bytes=data.file_size_bytes,
        sha256=data.sha256,
        storage_key=data.storage_key,
        page_count=data.page_count,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document


def get_document(
    db: Session,
    document_id: UUID,
    owner_id: UUID,
) -> Document | None:
    return db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.owner_id == owner_id,
        )
    )


def list_documents(
    db: Session,
    owner_id: UUID,
    limit: int,
    offset: int,
    status: str | None = None,
) -> tuple[list[Document], int]:
    filters = [Document.owner_id == owner_id]

    if status is not None:
        filters.append(Document.status == status)

    items = list(
        db.scalars(
            select(Document)
            .where(*filters)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    )

    total = db.scalar(
        select(func.count())
        .select_from(Document)
        .where(*filters)
    ) or 0

    return items, total


def update_document(
    db: Session,
    document: Document,
    data: DocumentUpdate,
) -> Document:
    if data.title is not None:
        document.title = data.title

    if data.status is not None:
        document.status = transition_status(document.status, data.status)

    if data.error_message is not None:
        document.error_message = data.error_message

    db.commit()
    db.refresh(document)
    return document


def delete_document(db: Session, document: Document) -> None:
    db.delete(document)
    db.commit()
