import pytest


def create_user(client, email: str, full_name: str) -> dict:
    response = client.post(
        "/users",
        json={
            "email": email,
            "full_name": full_name,
        },
    )
    assert response.status_code == 201
    return response.json()


def create_document(client, user_id: str, title: str) -> dict:
    response = client.post(
        "/documents",
        headers={"X-Dev-User-Id": user_id},
        json={
            "title": title,
            "original_filename": f"{title}.pdf",
            "content_type": "application/pdf",
            "file_size_bytes": 1234,
            "sha256": "a" * 64,
            "page_count": 2,
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.integration
def test_user_creation_and_current_user(client, clean_database):
    user = create_user(
        client,
        "integration-user@example.com",
        "Integration User",
    )

    response = client.get(
        "/users/me",
        headers={"X-Dev-User-Id": user["id"]},
    )

    assert response.status_code == 200
    assert response.json()["id"] == user["id"]
    assert response.json()["email"] == "integration-user@example.com"
    assert response.json()["role"] == "member"


@pytest.mark.integration
def test_duplicate_email_returns_409(client, clean_database):
    create_user(
        client,
        "duplicate@example.com",
        "First User",
    )

    response = client.post(
        "/users",
        json={
            "email": "duplicate@example.com",
            "full_name": "Second User",
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Email already exists"}


@pytest.mark.integration
def test_invalid_document_payload_returns_422(client, clean_database):
    user = create_user(
        client,
        "validation@example.com",
        "Validation User",
    )

    response = client.post(
        "/documents",
        headers={"X-Dev-User-Id": user["id"]},
        json={
            "title": "",
            "original_filename": "invalid.pdf",
            "content_type": "application/pdf",
        },
    )

    assert response.status_code == 422


@pytest.mark.integration
def test_missing_dev_identity_returns_401(client, clean_database):
    response = client.get("/users/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing X-Dev-User-Id header"}


@pytest.mark.integration
def test_document_crud_and_status_transitions(client, clean_database):
    user = create_user(
        client,
        "crud@example.com",
        "CRUD User",
    )

    document = create_document(client, user["id"], "CRUD Document")
    document_id = document["id"]

    assert document["status"] == "pending"
    assert document["owner_id"] == user["id"]

    response = client.get(
        f"/documents/{document_id}",
        headers={"X-Dev-User-Id": user["id"]},
    )
    assert response.status_code == 200
    assert response.json()["id"] == document_id

    response = client.patch(
        f"/documents/{document_id}",
        headers={"X-Dev-User-Id": user["id"]},
        json={"title": "Updated Document"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Document"

    response = client.patch(
        f"/documents/{document_id}",
        headers={"X-Dev-User-Id": user["id"]},
        json={"status": "processing"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "processing"

    response = client.patch(
        f"/documents/{document_id}",
        headers={"X-Dev-User-Id": user["id"]},
        json={"status": "ready"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ready"

    response = client.patch(
        f"/documents/{document_id}",
        headers={"X-Dev-User-Id": user["id"]},
        json={"status": "processing"},
    )
    assert response.status_code == 409

    response = client.delete(
        f"/documents/{document_id}",
        headers={"X-Dev-User-Id": user["id"]},
    )
    assert response.status_code == 204

    response = client.get(
        f"/documents/{document_id}",
        headers={"X-Dev-User-Id": user["id"]},
    )
    assert response.status_code == 404


@pytest.mark.integration
def test_document_pagination(client, clean_database):
    user = create_user(
        client,
        "pagination@example.com",
        "Pagination User",
    )

    for number in range(3):
        create_document(
            client,
            user["id"],
            f"Pagination Document {number}",
        )

    response = client.get(
        "/documents?limit=2&offset=0",
        headers={"X-Dev-User-Id": user["id"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["limit"] == 2
    assert body["offset"] == 0
    assert len(body["items"]) == 2

    response = client.get(
        "/documents?limit=2&offset=2",
        headers={"X-Dev-User-Id": user["id"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["limit"] == 2
    assert body["offset"] == 2
    assert len(body["items"]) == 1


@pytest.mark.integration
def test_document_isolation_between_users(client, clean_database):
    user_a = create_user(
        client,
        "user-a@example.com",
        "User A",
    )
    user_b = create_user(
        client,
        "user-b@example.com",
        "User B",
    )

    document_a = create_document(
        client,
        user_a["id"],
        "User A Document",
    )

    response = client.get(
        f"/documents/{document_a['id']}",
        headers={"X-Dev-User-Id": user_b["id"]},
    )
    assert response.status_code == 404

    response = client.patch(
        f"/documents/{document_a['id']}",
        headers={"X-Dev-User-Id": user_b["id"]},
        json={"title": "Unauthorized Update"},
    )
    assert response.status_code == 404

    response = client.delete(
        f"/documents/{document_a['id']}",
        headers={"X-Dev-User-Id": user_b["id"]},
    )
    assert response.status_code == 404

    response = client.get(
        "/documents",
        headers={"X-Dev-User-Id": user_b["id"]},
    )
    assert response.status_code == 200
    assert response.json()["items"] == []
    assert response.json()["total"] == 0
