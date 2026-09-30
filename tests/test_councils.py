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


class TestCouncilContactPost:
    """Test the contact_post_id foreign key on councils"""

    @pytest.fixture
    def post(self, db_session):
        """A post in a freshly created council."""
        from db_models.council_model import Council_DB
        from db_models.post_model import Post_DB

        council = Council_DB(**council_data_factory())
        db_session.add(council)
        db_session.commit()
        post = Post_DB(name_sv="Ordförande", name_en="Chairperson", council_id=council.id)
        db_session.add(post)
        db_session.commit()
        return post

    @pytest.fixture
    def council(self, db_session, post):
        """A council whose contact post is already set."""
        post.council.contact_post = post
        db_session.commit()
        return post.council

    def test_set_contact_post(self, client, admin_token, post):
        """Contact post can be set and is returned when reading the council."""
        response = update_council(client, post.council_id, admin_token, contact_post_id=post.id)

        assert response.status_code == 200
        assert response.json()["contact_post"]["id"] == post.id
        assert get_council(client, post.council_id, admin_token).json()["contact_post"]["name_en"] == "Chairperson"

    def test_clear_contact_post_with_explicit_null(self, client, admin_token, db_session, council):
        """Explicitly sending null clears the contact post, unlike other fields."""
        response = update_council(client, council.id, admin_token, contact_post_id=None)

        assert response.status_code == 200
        assert response.json()["contact_post"] is None
        db_session.refresh(council)
        assert council.contact_post_id is None

    def test_omitting_contact_post_leaves_it_untouched(self, client, admin_token, council):
        """A patch that does not mention contact_post_id must not clear it."""
        response = update_council(client, council.id, admin_token, name_en="Renamed Council")

        assert response.status_code == 200
        assert response.json()["name_en"] == "Renamed Council"
        assert response.json()["contact_post"]["id"] == council.contact_post_id

    def test_set_contact_post_to_missing_post(self, client, admin_token, council):
        """An unknown post id is a 404, not a foreign key violation."""
        response = update_council(client, council.id, admin_token, contact_post_id=99999)

        assert response.status_code == 404
        assert "Post not found" in response.json()["detail"]

    def test_create_council_with_contact_post_is_rejected(self, client, admin_token):
        """A new council owns no posts yet, so a contact post cannot be set on creation."""
        response = create_council(client, admin_token, name_sv="Bad Contact", contact_post_id=99999)

        assert response.status_code == 400
        assert "must belong to the council" in response.json()["detail"]

    def test_set_contact_post_from_another_council(self, client, admin_token, post):
        """A post owned by a different council cannot be used as contact post."""
        other = create_council(client, admin_token, name_sv="Annat utskott", name_en="Other Council").json()
        response = update_council(client, other["id"], admin_token, contact_post_id=post.id)

        assert response.status_code == 400
        assert "does not belong to this council" in response.json()["detail"]

    def test_deleting_contact_post_keeps_council(self, client, admin_token, db_session, council):
        """Deleting the contact post must clear the reference, not delete the council."""
        from db_models.council_model import Council_DB
        from db_models.post_model import Post_DB

        council_id, post_id = council.id, council.contact_post_id

        response = client.delete(f"/posts/{post_id}", headers=auth_headers(admin_token))
        assert response.status_code == 204

        db_session.expire_all()
        assert db_session.query(Post_DB).filter_by(id=post_id).one_or_none() is None
        surviving = db_session.query(Council_DB).filter_by(id=council_id).one_or_none()
        assert surviving is not None, "council must survive deletion of its contact post"
        assert surviving.contact_post_id is None
