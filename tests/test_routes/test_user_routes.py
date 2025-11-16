from __future__ import annotations

from uuid import UUID

from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND


def test_user_endpoints_crud_flow(api_client):
    payload = {"username": "api_user", "email": "api_user@example.com", "description": "Создан через API"}
    response = api_client.post("/users", json=payload)
    assert response.status_code == HTTP_201_CREATED

    body = response.json()
    user_id = UUID(body["id"])
    assert body["username"] == payload["username"]

    response = api_client.get(f"/users/{user_id}")
    assert response.status_code == HTTP_200_OK
    assert response.json()["email"] == payload["email"]

    response = api_client.get("/users")
    assert response.status_code == HTTP_200_OK
    listing = response.json()
    assert listing["total"] == 1
    assert listing["items"][0]["id"] == str(user_id)

    update_payload = {"username": "api_user_updated", "email": "api_user@example.com", "description": "Обновлено"}
    response = api_client.put(f"/users/{user_id}", json=update_payload)
    assert response.status_code == HTTP_200_OK
    assert response.json()["username"] == "api_user_updated"

    response = api_client.delete(f"/users/{user_id}")
    assert response.status_code == HTTP_204_NO_CONTENT

    response = api_client.get(f"/users/{user_id}")
    assert response.status_code == HTTP_404_NOT_FOUND


def test_user_listing_supports_multiple_entries(api_client):
    for idx in range(3):
        api_client.post(
            "/users",
            json={
                "username": f"bulk_{idx}",
                "email": f"bulk_{idx}@example.com",
                "description": None,
            },
        )

    response = api_client.get("/users", params={"count": 2, "page": 1})
    assert response.status_code == HTTP_200_OK
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
