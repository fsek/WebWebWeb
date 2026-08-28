# type: ignore
import pytest
from .basic_factories import auth_headers, song_data


class TestCreateSong:
    """Test POST /songs/ endpoint"""

    def test_create_song_success(self, client, admin_token, song_category):
        data = song_data(song_category["id"])
        response = client.post("/songs/", json=data, headers=auth_headers(admin_token))

        assert response.status_code in (200, 201), response.text
        created = response.json()
        assert created["title"] == data["title"]
        assert created["author"] == data["author"]
        assert created["content"] == data["content"]
        assert created["category"]["id"] == song_category["id"]
        assert created["views"] == 0

    def test_create_song_duplicate_title_is_rejected(self, client, admin_token, song):
        response = client.post(
            "/songs/",
            json=song_data(song["category"]["id"]),
            headers=auth_headers(admin_token),
        )

        assert response.status_code == 400

    def test_create_song_duplicate_title_is_case_insensitive(self, client, admin_token, song):
        response = client.post(
            "/songs/",
            json=song_data(song["category"]["id"], title=song["title"].upper()),
            headers=auth_headers(admin_token),
        )

        assert response.status_code == 400

    @pytest.mark.parametrize("token_fixture", ["member_token", "non_member_token"])
    def test_create_song_forbidden(self, client, request, song_category, token_fixture):
        response = client.post(
            "/songs/",
            json=song_data(song_category["id"]),
            headers=auth_headers(request.getfixturevalue(token_fixture)),
        )

        assert response.status_code == 403

    def test_create_song_unauthenticated(self, client, song_category):
        response = client.post("/songs/", json=song_data(song_category["id"]))

        assert response.status_code == 401


class TestGetSongs:
    """Test GET /songs/ and GET /songs/{song_id} endpoints"""

    def test_get_all_songs(self, client, song):
        response = client.get("/songs/")

        assert response.status_code == 200
        assert song["id"] in [listed["id"] for listed in response.json()]

    def test_get_single_song_increments_views(self, client, song):
        response = client.get(f"/songs/{song['id']}")

        assert response.status_code == 200
        assert response.json()["title"] == song["title"]
        assert response.json()["views"] == 1

    def test_get_missing_song(self, client):
        response = client.get("/songs/999999")

        assert response.status_code == 404


class TestUpdateSong:
    """Test PATCH /songs/{song_id} endpoint"""

    def test_update_song_success(self, client, admin_token, song):
        response = client.patch(
            f"/songs/{song['id']}",
            json=song_data(
                song["category"]["id"],
                title="Updated Song",
                author=None,
                melody=None,
                content="Updated lyrics",
            ),
            headers=auth_headers(admin_token),
        )

        assert response.status_code == 200
        updated = response.json()
        assert updated["title"] == "Updated Song"
        assert updated["content"] == "Updated lyrics"
        assert updated["author"] == song["author"]
        assert updated["melody"] is None

    def test_update_song_keeping_own_title(self, client, admin_token, song):
        response = client.patch(
            f"/songs/{song['id']}",
            json=song_data(song["category"]["id"], title=song["title"], content="Updated lyrics"),
            headers=auth_headers(admin_token),
        )

        assert response.status_code == 200, response.text
        assert response.json()["title"] == song["title"]
        assert response.json()["content"] == "Updated lyrics"

    def test_update_song_duplicate_title_is_rejected(self, client, admin_token, song, song_category):
        other = client.post(
            "/songs/",
            json=song_data(song_category["id"], title="Other Song"),
            headers=auth_headers(admin_token),
        ).json()

        response = client.patch(
            f"/songs/{other['id']}",
            json=song_data(song_category["id"], title=song["title"].upper()),
            headers=auth_headers(admin_token),
        )

        assert response.status_code == 400

    def test_update_song_forbidden(self, client, member_token, song):
        response = client.patch(
            f"/songs/{song['id']}",
            json=song_data(song["category"]["id"], title="Forbidden Update"),
            headers=auth_headers(member_token),
        )

        assert response.status_code == 403


class TestDeleteSong:
    """Test DELETE /songs/{song_id} endpoint"""

    def test_delete_song_success(self, client, admin_token, song):
        response = client.delete(f"/songs/{song['id']}", headers=auth_headers(admin_token))

        assert response.status_code == 200
        assert client.get(f"/songs/{song['id']}").status_code == 404

    def test_delete_song_forbidden(self, client, member_token, song):
        response = client.delete(f"/songs/{song['id']}", headers=auth_headers(member_token))

        assert response.status_code == 403

    def test_delete_category_detaches_song(self, client, admin_token, song, song_category):
        response = client.delete(f"/songs-category/{song_category['id']}", headers=auth_headers(admin_token))

        assert response.status_code == 200
        song_response = client.get(f"/songs/{song['id']}")
        assert song_response.status_code == 200
        assert song_response.json()["category"] is None
