# type: ignore
from sqlalchemy.exc import IntegrityError
from db_models.prereg_member_model import PreregMember_DB
from tests.basic_factories import auth_headers
import pytest


def create_db_prereg_member(db_session, telephone_number=None, stil_id=None, email=None):
    member = PreregMember_DB(telephone_number=telephone_number, stil_id=stil_id, email=email)
    db_session.add(member)
    db_session.commit()
    return member


def test_get_all_prereg_member_info(client, admin_token, db_session):
    create_db_prereg_member(db_session, email="test1@example.com")
    create_db_prereg_member(db_session, stil_id="xy9876zw-s")

    resp = client.get("/prereg-members/", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2


def test_get_prereg_member_info(client, admin_token, db_session):
    member = create_db_prereg_member(db_session, email="wow@cool.com")

    resp = client.get(f"/prereg-members/{member.prereg_member_id}", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert resp.json()["email"] == "wow@cool.com"


def test_create_prereg_member(client, admin_token):
    payload = {"telephone_number": "+46234567890", "stil_id": "ab1234cd-s", "email": "user@test.com"}
    resp = client.post("/prereg-members/", json=payload, headers=auth_headers(admin_token))
    assert resp.status_code in [200, 201]
    data = resp.json()
    assert data["email"] == "user@test.com"
    assert "prereg_member_id" in data


def test_create_prereg_member_missing_identifiers(client, admin_token):
    payload = {"telephone_number": None, "stil_id": None, "email": None}
    resp = client.post("/prereg-members/", json=payload, headers=auth_headers(admin_token))
    assert resp.status_code == 400


def test_create_prereg_member_invalid_identifiers(client, admin_token):
    payload = {"telephone_number": "number", "stil_id": None, "email": None}
    resp1 = client.post("/prereg-members/", json=payload, headers=auth_headers(admin_token))
    assert resp1.status_code in [400, 422]
    payload = {"telephone_number": None, "stil_id": "asdsaddasads", "email": None}
    resp2 = client.post("/prereg-members/", json=payload, headers=auth_headers(admin_token))
    assert resp2.status_code in [400, 422]
    payload = {"telephone_number": None, "stil_id": None, "email": "wow"}
    resp3 = client.post("/prereg-members/", json=payload, headers=auth_headers(admin_token))
    assert resp3.status_code in [400, 422]


def test_create_duplicate_prereg_member_fails(client, admin_token, db_session):
    create_db_prereg_member(db_session, telephone_number="+46234567890", stil_id="ef5678gh-s", email="555@test.com")
    db_session.commit()
    payload = {"telephone_number": "+46234567890", "stil_id": "ef5678gh-s", "email": "555@test.com"}
    resp = client.post("/prereg-members/", json=payload, headers=auth_headers(admin_token))
    assert resp.status_code in [400, 409]


def test_create_multiple_prereg_members(client, admin_token, db_session):
    existing = create_db_prereg_member(
        db_session, telephone_number="+46234567890", stil_id="ij1234kl-s", email="999@test.com"
    )
    db_session.commit()
    payload = [
        {
            "telephone_number": "+46234567890",
            "stil_id": "ij1234kl-s",
            "email": "999@test.com",
        },  # duplicate (will be skipped)
        {"telephone_number": "+46234567890", "stil_id": "mn5678op-s", "email": "888@test.com"},  # new
        {"telephone_number": "+46234567890", "stil_id": "qr9012st-s", "email": "777@test.com"},  # new
    ]
    resp = client.post("/prereg-members/multiple", json=payload, headers=auth_headers(admin_token))
    assert resp.status_code in [200, 201]
    data = resp.json()
    # one collision returned (existing), others created — ensure collision present
    assert any(d["prereg_member_id"] == existing.prereg_member_id for d in data)


def test_create_multiple_prereg_members_all_exist_fails(client, admin_token, db_session):
    create_db_prereg_member(db_session, telephone_number="+46234567890", stil_id="uv3456wx-s", email="999@test.com")
    db_session.commit()
    payload = [{"telephone_number": "+46234567890", "stil_id": "uv3456wx-s", "email": "999@test.com"}]
    resp = client.post("/prereg-members/multiple", json=payload, headers=auth_headers(admin_token))
    assert resp.status_code == 400


def test_update_prereg_member(client, admin_token, db_session):
    member = create_db_prereg_member(db_session, email="old@test.com")
    payload = {"email": "new@test.com"}
    resp = client.patch(f"/prereg-members/{member.prereg_member_id}", json=payload, headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert resp.json()["email"] == "new@test.com"


def test_update_prereg_member_partial_update_preserves_other_fields(client, admin_token, db_session):
    member = create_db_prereg_member(
        db_session, telephone_number="+46701234567", stil_id="pq1234rs-s", email="old@test.com"
    )
    before = client.get(f"/prereg-members/{member.prereg_member_id}", headers=auth_headers(admin_token)).json()
    payload = {"email": "new@test.com"}
    resp = client.patch(f"/prereg-members/{member.prereg_member_id}", json=payload, headers=auth_headers(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "new@test.com"
    assert data["telephone_number"] == before["telephone_number"]
    assert data["stil_id"] == "pq1234rs-s"


def test_update_prereg_member_remove_all_identifiers_fails(client, admin_token, db_session):
    member = create_db_prereg_member(db_session, email="old@test.com")
    payload = {"telephone_number": None, "email": None}
    resp = client.patch(f"/prereg-members/{member.prereg_member_id}", json=payload, headers=auth_headers(admin_token))
    assert resp.status_code == 400


def test_delete_prereg_member(client, admin_token, db_session):
    member = create_db_prereg_member(db_session, email="delete@test.com")
    resp = client.delete(f"/prereg-members/{member.prereg_member_id}", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert resp.json()["prereg_member_id"] == member.prereg_member_id


def test_delete_multiple_prereg_members(client, admin_token, db_session):
    m1 = create_db_prereg_member(db_session, email="m1@test.com")
    m2 = create_db_prereg_member(db_session, email="m2@test.com")

    payload = [m1.prereg_member_id, m2.prereg_member_id]
    resp = client.request("DELETE", "/prereg-members/multiple", json=payload, headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.parametrize(
    "identifiers",
    [
        pytest.param({"email": "nnd@test.com"}, id="email_only"),
        pytest.param({"telephone_number": "+46701112233"}, id="telephone_only"),
        pytest.param({"stil_id": "ab1234cd-s"}, id="stil_id_only"),
        pytest.param({"telephone_number": "+46701112244", "email": "nnd2@test.com"}, id="two_of_three"),
        pytest.param(
            {"telephone_number": "+46705556677", "stil_id": "ef5678gh-s", "email": "full@test.com"}, id="no_nulls"
        ),
    ],
)
def test_unique_all_rejects_duplicates(db_session, identifiers):
    """
    unique_all must reject a duplicate even when the unset identifiers are NULL.

    Postgres defaults to NULLS DISTINCT, where any NULL in the key makes rows non-conflicting.
    Without postgresql_nulls_not_distinct on the constraint, every case but no_nulls is let in.
    """
    db_session.add(PreregMember_DB(**identifiers))
    db_session.flush()

    with pytest.raises(IntegrityError):  # Check if a second insert has the db raise a duplicate error
        db_session.add(PreregMember_DB(**identifiers))
        db_session.flush()


def test_unique_all_allows_members_differing_in_one_identifier(db_session):
    """Guard against over-tightening: NULLS NOT DISTINCT must not collapse genuinely different rows."""
    db_session.add(PreregMember_DB(email="distinct1@test.com"))
    db_session.add(PreregMember_DB(email="distinct2@test.com"))
    db_session.add(PreregMember_DB(telephone_number="+46708889900", email="distinct1@test.com"))
    db_session.flush()

    assert db_session.query(PreregMember_DB).count() == 3
