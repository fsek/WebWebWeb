# type: ignore
from fastapi import status

from .basic_factories import auth_headers


def keyval_data_factory(**kwargs):
    default_data = {
        "key": "site_name",
        "value": "F-sektionen",
    }
    return {**default_data, **kwargs}


def create_keyval(client, token=None, **kwargs):
    headers = auth_headers(token) if token else {}
    return client.post("/keyvals/", json=keyval_data_factory(**kwargs), headers=headers)


def test_get_keyvals_returns_empty_list_initially(client):
    response = client.get("/keyvals/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_keyval_not_found(client):
    response = client.get("/keyvals/missing-key")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_keyval_unauthenticated_denied(client):
    response = create_keyval(client, key="unauth-key", value="nope")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_keyval_member_forbidden(client, member_token):
    response = create_keyval(client, member_token, key="member-key", value="nope")
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_and_get_keyval(client, admin_token):
    create_response = create_keyval(client, admin_token, key="welcome_text", value="Hello")
    assert create_response.status_code == status.HTTP_200_OK
    assert create_response.json() == {"key": "welcome_text", "value": "Hello"}

    get_response = client.get("/keyvals/welcome_text")
    assert get_response.status_code == status.HTTP_200_OK
    assert get_response.json() == {"key": "welcome_text", "value": "Hello"}

    list_response = client.get("/keyvals/")
    assert list_response.status_code == status.HTTP_200_OK
    assert any(item["key"] == "welcome_text" and item["value"] == "Hello" for item in list_response.json())


def test_create_duplicate_keyval_returns_400(client, admin_token):
    first_response = create_keyval(client, admin_token, key="duplicate-key", value="first")
    assert first_response.status_code == status.HTTP_200_OK

    second_response = create_keyval(client, admin_token, key="duplicate-key", value="second")
    assert second_response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_and_delete_keyval(client, admin_token):
    create_response = create_keyval(client, admin_token, key="theme", value="light")
    assert create_response.status_code == status.HTTP_200_OK

    update_response = client.patch(
        "/keyvals/theme",
        json={"value": "dark"},
        headers=auth_headers(admin_token),
    )
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json() == {"key": "theme", "value": "dark"}

    delete_response = client.delete("/keyvals/theme", headers=auth_headers(admin_token))
    assert delete_response.status_code == status.HTTP_200_OK
    assert delete_response.json() == {"key": "theme", "value": "dark"}

    get_deleted_response = client.get("/keyvals/theme")
    assert get_deleted_response.status_code == status.HTTP_404_NOT_FOUND
