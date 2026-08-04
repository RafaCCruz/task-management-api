"""Tests for task CRUD endpoints."""


def test_create_task(client, auth_headers):
    response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={
            "title": "Write unit tests",
            "description": "Cover auth and tasks",
            "priority": "high",
            "status": "pending",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Write unit tests"
    assert data["priority"] == "high"
    assert data["status"] == "pending"
    assert "id" in data
    assert "owner_id" in data


def test_list_tasks_empty(client, auth_headers):
    response = client.get("/api/v1/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1


def test_list_tasks_with_filters(client, auth_headers):
    # Create a few tasks
    client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={"title": "High priority", "priority": "high", "status": "pending"},
    )
    client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={"title": "Low priority", "priority": "low", "status": "completed"},
    )

    # Filter by priority
    response = client.get(
        "/api/v1/tasks",
        headers=auth_headers,
        params={"priority": "high"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["priority"] == "high"

    # Search
    response = client.get(
        "/api/v1/tasks",
        headers=auth_headers,
        params={"search": "High"},
    )
    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_get_task(client, auth_headers):
    create = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={"title": "Detail me"},
    )
    task_id = create.json()["id"]

    response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Detail me"


def test_get_nonexistent_task(client, auth_headers):
    response = client.get("/api/v1/tasks/99999", headers=auth_headers)
    assert response.status_code == 404


def test_update_task(client, auth_headers):
    create = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={"title": "Original title"},
    )
    task_id = create.json()["id"]

    response = client.patch(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
        json={"title": "Updated title", "status": "in_progress"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"
    assert data["status"] == "in_progress"


def test_delete_task(client, auth_headers):
    create = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={"title": "To be deleted"},
    )
    task_id = create.json()["id"]

    response = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 204

    # Confirm it's gone
    get_resp = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_resp.status_code == 404


def test_tasks_require_auth(client):
    response = client.get("/api/v1/tasks")
    assert response.status_code == 401
