import pytest

from backend.app.services.state_machine import (
    InvalidDocumentStatusTransition,
    transition_status,
)


@pytest.mark.unit
@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("pending", "processing"),
        ("processing", "ready"),
        ("processing", "failed"),
        ("failed", "pending"),
    ],
)
def test_valid_document_status_transitions(current: str, target: str) -> None:
    assert transition_status(current, target) == target


@pytest.mark.unit
@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("pending", "ready"),
        ("pending", "failed"),
        ("processing", "pending"),
        ("ready", "processing"),
        ("ready", "failed"),
        ("failed", "ready"),
    ],
)
def test_invalid_document_status_transitions(
    current: str,
    target: str,
) -> None:
    with pytest.raises(InvalidDocumentStatusTransition):
        transition_status(current, target)
