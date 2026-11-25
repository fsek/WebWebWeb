# type: ignore
from fastapi import status

from .basic_factories import auth_headers

URL = "/cafe-shifts/leaderboard-start"


def test_set_leaderboard_start_unauthenticated_denied(client):
    response = client.patch(URL, json={"starts_at": "2026-01-01T00:00:00Z"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_set_leaderboard_start_member_forbidden(client, member_token):
    response = client.patch(URL, json={"starts_at": "2026-01-01T00:00:00Z"}, headers=auth_headers(member_token))
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_set_and_update_leaderboard_start(client, admin_token):
    headers = auth_headers(admin_token)

    first = client.patch(URL, json={"starts_at": "2026-01-01T00:00:00Z"}, headers=headers)
    assert first.status_code == status.HTTP_200_OK
    assert first.json() == {"key": "cafe_leaderboard_start", "value": "2026-01-01T00:00:00+00:00"}

    second = client.patch(URL, json={"starts_at": "2026-02-15T12:30:00Z"}, headers=headers)
    assert second.status_code == status.HTTP_200_OK
    assert second.json()["value"] == "2026-02-15T12:30:00+00:00"

    public = client.get("/keyvals/cafe_leaderboard_start")
    assert public.status_code == status.HTTP_200_OK
    assert public.json()["value"] == "2026-02-15T12:30:00+00:00"


def test_set_leaderboard_start_invalid_body(client, admin_token):
    response = client.patch(URL, json={"starts_at": "not-a-date"}, headers=auth_headers(admin_token))
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
