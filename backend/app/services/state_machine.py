class InvalidDocumentStatusTransition(ValueError):
    """Raised when a document status transition is not allowed."""


ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "pending": {"processing"},
    "processing": {"ready", "failed"},
    "ready": set(),
    "failed": {"pending"},
}


def transition_status(current: str, target: str) -> str:
    if target not in ALLOWED_TRANSITIONS.get(current, set()):
        raise InvalidDocumentStatusTransition(
            f"Invalid document status transition: {current} -> {target}"
        )

    return target
