# type: ignore
from .basic_factories import auth_headers, council_data_factory, create_council
import pytest


def get_council(client, council_id, token=None):
    headers = auth_headers(token) if token else {}
    return client.get(f"/councils/{council_id}", headers=headers)


def get_all_councils(client, token=None):
    headers = auth_headers(token) if token else {}
    return client.get("/councils/", headers=headers)


def update_council(client, council_id, token=None, **kwargs):
    headers = auth_headers(token) if token else {}
    return client.patch(f"/councils/update_council/{council_id}", json=kwargs, headers=headers)


def assert_council_fields(data, expected):
    for field, value in expected.items():
        assert data[field] == value


class TestCreateCouncil:
    """Test POST /councils/ endpoint"""

    def test_create_council_success(self, client, admin_token):
        """Admin can create a council with bilingual fields."""
        response = create_council(client, admin_token)

        assert response.status_code in (200, 201)
        assert_council_fields(response.json(), council_data_factory())
        assert "id" in response.json()

    def test_create_council_duplicate_name(self, client, admin_token):
        """Duplicate Swedish name is rejected."""
        resp1 = create_council(client, admin_token, name_sv="Duplicate Council")
        assert resp1.status_code in (200, 201)
        resp2 = create_council(client, admin_token, name_sv="Duplicate Council")
        assert resp2.status_code == 400

    @pytest.mark.parametrize("token_fixture", ["member_token", "non_member_token"])
    def test_create_council_forbidden(self, client, request, token_fixture):
        """Members and non-members are forbidden from creating councils."""
        token = request.getfixturevalue(token_fixture)
        response = create_council(client, token)
        assert response.status_code == 403

    def test_create_council_unauthenticated(self, client):
        """Unauthenticated requests get 401."""
        response = create_council(client)
        assert response.status_code == 401


class TestGetAllCouncils:
    """Test GET /councils/ endpoint"""

    def setup_councils(self, db_session):
        from db_models.council_model import Council_DB

        councils = [
            Council_DB(
                name_sv="Första rådet",
                description_sv="Första beskrivningen",
                name_en="First Council",
                description_en="First description",
            ),
            Council_DB(
                name_sv="Andra rådet",
                description_sv="Andra beskrivningen",
                name_en="Second Council",
                description_en="Second description",
            ),
        ]
        db_session.add_all(councils)
        db_session.commit()
        return councils

    def test_get_all_councils_member(self, client, member_token, db_session):
        """Test that members can get all councils"""
        self.setup_councils(db_session)
        response = get_all_councils(client, member_token)

        assert response.status_code == 200
        council_names = [c["name_sv"] for c in response.json()]
        assert "Första rådet" in council_names
        assert "Andra rådet" in council_names

    def test_get_all_councils_admin(self, client, admin_token):
        """Test that admins can get all councils"""
        response = get_all_councils(client, admin_token)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    @pytest.mark.parametrize("token_fixture, expected_status", [("non_member_token", 403), (None, 401)])
    def test_get_all_councils_forbidden(self, client, request, token_fixture, expected_status):
        """Test that non-members and unauthenticated users cannot get councils"""
        token = request.getfixturevalue(token_fixture) if token_fixture else None
        response = get_all_councils(client, token)
        assert response.status_code == expected_status


class TestGetSingleCouncil:
    """Test GET /councils/{council_id} endpoint"""

    def create_and_get_id(self, db_session):
        from db_models.council_model import Council_DB

        council = Council_DB(
            name_sv="Test Council",
            description_sv="Test Description",
            name_en="Test Council EN",
            description_en="Test Description EN",
        )
        db_session.add(council)
        db_session.commit()
        return council.id, council

    def test_get_council_success(self, client, member_token, db_session):
        """Test successful retrieval of a single council"""
        council_id, council = self.create_and_get_id(db_session)
        response = get_council(client, council_id, member_token)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == council_id
        assert_council_fields(
            data,
            {
                "name_sv": council.name_sv,
                "description_sv": council.description_sv,
                "name_en": council.name_en,
                "description_en": council.description_en,
            },
        )

    @pytest.mark.parametrize(
        "token_fixture, expected_statuses",
        [("member_token", (200, 404)), ("non_member_token", (401, 403)), (None, (401,))],
    )
    def test_get_council_access(self, client, request, token_fixture, expected_statuses):
        """Test access to council details for different user types using fixture values."""
        council_id = 1
        token = request.getfixturevalue(token_fixture) if token_fixture else None
        response = get_council(client, council_id, token)
        assert response.status_code in expected_statuses

    def test_get_council_not_found(self, client, member_token):
        """Test getting non-existent council returns 404"""
        response = get_council(client, 99999, member_token)
        assert response.status_code == 404


class TestUpdateCouncil:
    """Test PATCH /councils/update_council/{council_id} endpoint"""

    def create_and_get_id(self, db_session):
        from db_models.council_model import Council_DB

        council = Council_DB(
            name_sv="Original Name",
            description_sv="Original Description",
            name_en="Original Name EN",
            description_en="Original Description EN",
        )
        db_session.add(council)
        db_session.commit()
        return council.id, council

    def test_update_council_success(self, client, admin_token, db_session):
        """Test successful council update by admin"""
        council_id, council = self.create_and_get_id(db_session)
        update_data = {"name_sv": "Updated Name", "description_en": "Updated Description EN"}
        response = update_council(client, council_id, admin_token, **update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name_sv"] == "Updated Name"
        assert data["description_sv"] == "Original Description"
        assert data["name_en"] == "Original Name EN"
        assert data["description_en"] == "Updated Description EN"

    def test_update_council_not_found(self, client, admin_token):
        """Test updating non-existent council returns 404"""
        update_data = {"name_sv": "New Name"}
        response = update_council(client, 99999, admin_token, **update_data)

        assert response.status_code == 404
        assert "Council not found" in response.json()["detail"]

    @pytest.mark.parametrize(
        "token_fixture, expected_status", [("member_token", 403), ("non_member_token", 403), (None, 401)]
    )
    def test_update_council_forbidden(self, client, request, token_fixture, expected_status, db_session):
        """Test that regular members and non-members cannot update councils"""
        council_id, _ = self.create_and_get_id(db_session)
        update_data = {"name_sv": "Forbidden Update"}
        token = request.getfixturevalue(token_fixture) if token_fixture else None
        response = update_council(client, council_id, token, **update_data)
        assert response.status_code == expected_status

    def test_update_council_partial(self, client, admin_token, db_session):
        """Test partial updates only change specified fields"""
        council_id, council = self.create_and_get_id(db_session)
        update_data = {"name_en": "Updated English Only"}
        response = update_council(client, council_id, admin_token, **update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name_sv"] == council.name_sv
        assert data["description_sv"] == council.description_sv
        assert data["name_en"] == "Updated English Only"
        assert data["description_en"] == council.description_en

    def test_update_council_none_values_ignored(self, client, admin_token, db_session):
        """Test that None values in update data are ignored"""
        council_id, council = self.create_and_get_id(db_session)
        update_data = {
            "name_sv": "Updated Name",
            "description_sv": None,
            "name_en": None,
            "description_en": "Updated Description EN",
        }
        response = update_council(client, council_id, admin_token, **update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name_sv"] == "Updated Name"
        assert data["description_sv"] == council.description_sv
        assert data["name_en"] == council.name_en
        assert data["description_en"] == "Updated Description EN"
        # Send update with None values
        update_data = {
            "name_sv": "Updated Name",
            "description_sv": None,
            "name_en": None,
            "description_en": "Updated Description EN",
        }

        response = client.patch(
            f"/councils/update_council/{council.id}", json=update_data, headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name_sv"] == "Updated Name"
        assert data["description_sv"] == "Original Description"  # Should remain unchanged
        assert data["name_en"] == "Original Name EN"  # Should remain unchanged
        assert data["description_en"] == "Updated Description EN"
        response = client.patch(
            f"/councils/update_council/{council.id}", json=update_data, headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name_sv"] == "Original Swedish"  # Unchanged
        assert data["description_sv"] == "Original Swedish Description"  # Unchanged
        assert data["name_en"] == "Updated English Only"  # Changed
        assert data["description_en"] == "Original English Description"  # Unchanged

    def test_update_council_none_values_ignored(self, client, admin_token, db_session):
        """Test that None values in update data are ignored"""
        from db_models.council_model import Council_DB

        council = Council_DB(
            name_sv="Original Name",
            description_sv="Original Description",
            name_en="Original Name EN",
            description_en="Original Description EN",
        )
        db_session.add(council)
        db_session.commit()

        # Send update with None values
        update_data = {
            "name_sv": "Updated Name",
            "description_sv": None,
            "name_en": None,
            "description_en": "Updated Description EN",
        }

        response = client.patch(
            f"/councils/update_council/{council.id}", json=update_data, headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name_sv"] == "Updated Name"
        assert data["description_sv"] == "Original Description"  # Should remain unchanged
        assert data["name_en"] == "Original Name EN"  # Should remain unchanged
        assert data["description_en"] == "Updated Description EN"
