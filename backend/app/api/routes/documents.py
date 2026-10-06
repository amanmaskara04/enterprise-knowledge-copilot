from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.app.db.session import get_db
from backend.app.models.document import Document
from backend.app.models.user import User
from backend.app.schemas.document import DocumentCreate, DocumentRead, DocumentUpdate
from backend.app.schemas.pagination import Page
from backend.app.services.document import (
    create_document,
    delete_document,
    get_document,
    list_documents,
    update_document,
)
from backend.app.services.state_machine import InvalidDocumentStatusTransition

router = APIRouter()


@router.post(
    "/documents",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_document_endpoint(
    data: DocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Document:
    return create_document(db, current_user.id, data)


@router.get("/documents", response_model=Page[DocumentRead])
def list_documents_endpoint(
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status_filter: str | None = Query(default=None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Page[DocumentRead]:
    items, total = list_documents(
        db,
        current_user.id,
        limit,
        offset,
        status_filter,
    )
    return Page(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/documents/{document_id}", response_model=DocumentRead)
def get_document_endpoint(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Document:
    document = get_document(db, document_id, current_user.id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    return document


@router.patch("/documents/{document_id}", response_model=DocumentRead)
def update_document_endpoint(
    document_id: UUID,
    data: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Document:
    document = get_document(db, document_id, current_user.id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    try:
        return update_document(db, document, data)
    except InvalidDocumentStatusTransition as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document_endpoint(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    document = get_document(db, document_id, current_user.id)
    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    delete_document(db, document)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
