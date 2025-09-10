# type: ignore
from .basic_factories import (
    auth_headers,
)


def nomination_data_factory(**kwargs):
    """Factory for creating nomination payloads with sensible defaults."""
    default_data = {
        "nominee_name": "Test Nominee",
        "nominee_email": "test.nominee@example.com",
        "motivation": "Motivated for the role",
        "election_post_id": 1,
    }
    return {**default_data, **kwargs}


def post_nomination(client, sub_election_id, token=None, **kwargs):
    """Helper to POST /nominations/{sub_election_id} with optional token and payload overrides."""
    data = nomination_data_factory(sub_election_id=sub_election_id, **kwargs)
    headers = auth_headers(token) if token else {}
    return client.post(f"/nominations/{sub_election_id}", json=data, headers=headers)


# Nomination tests
def test_member_create_nomination(member_token, client, admin_post, open_sub_election):
    nomination_data = nomination_data_factory(election_post_id=open_sub_election.election_posts[0].election_post_id)
    resp = post_nomination(client, open_sub_election.sub_election_id, member_token, **nomination_data)
    assert resp.status_code == 201, resp.text


def test_non_member_cannot_create_nomination(non_member_token, client, admin_post, open_sub_election):
    nomination_data = nomination_data_factory(election_post_id=open_sub_election.election_posts[0].election_post_id)
    resp = post_nomination(client, open_sub_election.sub_election_id, non_member_token, **nomination_data)
    assert resp.status_code == 403


def test_admin_get_election_nominations(admin_token, member_token, client, admin_post, open_sub_election):
    nomination_data = nomination_data_factory(
        nominee_name="Jane Smith",
        election_post_id=open_sub_election.election_posts[0].election_post_id,
    )
    create_resp = post_nomination(client, open_sub_election.sub_election_id, member_token, **nomination_data)
    assert create_resp.status_code == 201

    # Admin can view nominations for election
    resp = client.get(f"/nominations/election/{open_sub_election.election_id}", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    nominations = resp.json()
    assert len(nominations) >= 1
    assert any(n["nominee_name"] == "Jane Smith" for n in nominations)


def test_admin_get_sub_election_nominations(admin_token, member_token, client, admin_post, open_sub_election):
    nomination_data = nomination_data_factory(
        nominee_name="Bob Wilson",
        election_post_id=open_sub_election.election_posts[0].election_post_id,
    )
    create_resp = post_nomination(client, open_sub_election.sub_election_id, member_token, **nomination_data)
    assert create_resp.status_code == 201

    # Admin can view nominations for sub-election
    resp = client.get(
        f"/nominations/sub-election/{open_sub_election.sub_election_id}", headers=auth_headers(admin_token)
    )
    assert resp.status_code == 200
    nominations = resp.json()
    assert len(nominations) >= 1
    assert any(n["nominee_name"] == "Bob Wilson" for n in nominations)


def test_member_cannot_view_nominations(member_token, client, open_sub_election):
    # Member cannot view election nominations
    resp_election = client.get(
        f"/nominations/election/{open_sub_election.election_id}", headers=auth_headers(member_token)
    )
    assert resp_election.status_code == 403

    # Member cannot view sub-election nominations
    resp_sub = client.get(
        f"/nominations/sub-election/{open_sub_election.sub_election_id}", headers=auth_headers(member_token)
    )
    assert resp_sub.status_code == 403


def test_non_member_cannot_view_nominations(non_member_token, client, open_sub_election):
    # Non-member cannot view election nominations
    resp_election = client.get(
        f"/nominations/election/{open_sub_election.election_id}", headers=auth_headers(non_member_token)
    )
    assert resp_election.status_code == 403

    # Non-member cannot view sub-election nominations
    resp_sub = client.get(
        f"/nominations/sub-election/{open_sub_election.sub_election_id}", headers=auth_headers(non_member_token)
    )
    assert resp_sub.status_code == 403


def test_admin_delete_nomination(admin_token, member_token, client, admin_post, open_sub_election):
    nomination_data = nomination_data_factory(
        nominee_name="Alice Cooper",
        election_post_id=open_sub_election.election_posts[0].election_post_id,
    )
    create_resp = post_nomination(client, open_sub_election.sub_election_id, member_token, **nomination_data)
    assert create_resp.status_code == 201

    # Get nominations to find the ID
    get_resp = client.get(
        f"/nominations/sub-election/{open_sub_election.sub_election_id}", headers=auth_headers(admin_token)
    )
    nominations = get_resp.json()
    nomination_id = next(n["nomination_id"] for n in nominations if n["nominee_name"] == "Alice Cooper")

    # Admin can delete nomination
    del_resp = client.delete(f"/nominations/{nomination_id}", headers=auth_headers(admin_token))
    assert del_resp.status_code == 204

    # Verify nomination is deleted
    get_resp_after = client.get(
        f"/nominations/sub-election/{open_sub_election.sub_election_id}", headers=auth_headers(admin_token)
    )
    nominations_after = get_resp_after.json()
    assert not any(n["nominee_name"] == "Alice Cooper" for n in nominations_after)


def test_member_cannot_delete_nomination(admin_token, member_token, client, admin_post, open_sub_election):
    nomination_data = nomination_data_factory(election_post_id=open_sub_election.election_posts[0].election_post_id)
    create_resp = post_nomination(client, open_sub_election.sub_election_id, member_token, **nomination_data)
    assert create_resp.status_code == 201

    # Get nomination ID
    get_resp = client.get(
        f"/nominations/sub-election/{open_sub_election.sub_election_id}", headers=auth_headers(admin_token)
    )
    nominations = get_resp.json()
    nomination_id = next(n["nomination_id"] for n in nominations if n["nominee_name"] == "Test Nominee")

    # Member cannot delete nomination
    del_resp = client.delete(f"/nominations/{nomination_id}", headers=auth_headers(member_token))
    assert del_resp.status_code == 403


def test_nomination_response_structure(admin_token, member_token, client, admin_post, open_sub_election):
    nomination_data = nomination_data_factory(
        nominee_name="Structure Test",
        nominee_email="structure@example.com",
        motivation="Testing response structure",
        election_post_id=open_sub_election.election_posts[0].election_post_id,
    )
    create_resp = post_nomination(client, open_sub_election.sub_election_id, member_token, **nomination_data)
    assert create_resp.status_code == 201

    # Get nominations and verify structure
    get_resp = client.get(
        f"/nominations/sub-election/{open_sub_election.sub_election_id}", headers=auth_headers(admin_token)
    )
    nominations = get_resp.json()
    nomination = next(n for n in nominations if n["nominee_name"] == "Structure Test")

    # Verify all required fields are present
    required_fields = [
        "nomination_id",
        "sub_election_id",
        "nominee_name",
        "nominee_email",
        "motivation",
        "created_at",
        "post_id",
        "election_post_id",
    ]
    for field in required_fields:
        assert field in nomination, f"Missing field: {field}"

    assert nomination["nominee_name"] == "Structure Test"
    assert nomination["nominee_email"] == "structure@example.com"
    assert nomination["motivation"] == "Testing response structure"
    assert nomination["sub_election_id"] == open_sub_election.sub_election_id
