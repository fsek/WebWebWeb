# type: ignore
import pytest
from .basic_factories import auth_headers, category_data


class TestCreateSongCategory:
    """Test POST /songs-category/ endpoint"""

    def test_create_song_category_success(self, client, admin_token):
        response = client.post(
            "/songs-category/",
            json=category_data("Visor"),
            headers=auth_headers(admin_token),
        )

        assert response.status_code in (200, 201), response.text
        assert response.json()["name"] == "Visor"

    def test_create_song_category_duplicate_is_case_insensitive(self, client, admin_token, song_category):
        response = client.post(
            "/songs-category/",
            json=category_data(song_category["name"].upper()),
            headers=auth_headers(admin_token),
        )

        assert response.status_code == 400

    @pytest.mark.parametrize("token_fixture", ["member_token", "non_member_token"])
    def test_create_song_category_forbidden(self, client, request, token_fixture):
        response = client.post(
            "/songs-category/",
            json=category_data("Forbidden"),
            headers=auth_headers(request.getfixturevalue(token_fixture)),
        )

        assert response.status_code == 403

    def test_create_song_category_unauthenticated(self, client):
        response = client.post("/songs-category/", json=category_data("Unauthenticated"))

        assert response.status_code == 401


class TestGetSongCategories:
    """Test GET /songs-category/ and GET /songs-category/{category_id} endpoints"""

    def test_get_all_song_categories(self, client, song_category):
        response = client.get("/songs-category/")

        assert response.status_code == 200
        assert song_category["id"] in [category["id"] for category in response.json()]

    def test_get_single_song_category(self, client, song_category):
        response = client.get(f"/songs-category/{song_category['id']}")

        assert response.status_code == 200
        assert response.json() == song_category

    def test_get_missing_song_category(self, client):
        response = client.get("/songs-category/999999")

        assert response.status_code == 404


class TestUpdateSongCategory:
    """Test PATCH /songs-category/{category_id} endpoint"""

    def test_update_song_category_success(self, client, admin_token, song_category):
        response = client.patch(
            f"/songs-category/{song_category['id']}",
            json=category_data("Updated Category"),
            headers=auth_headers(admin_token),
        )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Category"

    def test_update_song_category_duplicate_is_case_insensitive(self, client, admin_token, song_category):
        other = client.post(
            "/songs-category/",
            json=category_data("Other Category"),
            headers=auth_headers(admin_token),
        ).json()

        response = client.patch(
            f"/songs-category/{other['id']}",
            json=category_data(song_category["name"].lower()),
            headers=auth_headers(admin_token),
        )

        assert response.status_code == 400

    def test_update_song_category_forbidden(self, client, member_token, song_category):
        response = client.patch(
            f"/songs-category/{song_category['id']}",
            json=category_data("Forbidden Update"),
            headers=auth_headers(member_token),
        )

        assert response.status_code == 403


class TestDeleteSongCategory:
    """Test DELETE /songs-category/{category_id} endpoint"""

    def test_delete_song_category_success(self, client, admin_token, song_category):
        response = client.delete(f"/songs-category/{song_category['id']}", headers=auth_headers(admin_token))

        assert response.status_code == 200
        assert client.get(f"/songs-category/{song_category['id']}").status_code == 404

    def test_delete_song_category_forbidden(self, client, member_token, song_category):
        response = client.delete(f"/songs-category/{song_category['id']}", headers=auth_headers(member_token))

        assert response.status_code == 403
