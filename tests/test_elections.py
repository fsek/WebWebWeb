# type: ignore
from .basic_factories import create_election, auth_headers, patch_election


def test_create_election(admin_token, client):
    resp = create_election(client, token=admin_token)
    assert resp.status_code in (200, 201), f"Create election failed: {resp.text}"
    election = resp.json()
    assert "election_id" in election


def test_retrieve_all_elections(admin_token, client):
    resp = create_election(client, token=admin_token)
    election_id = resp.json()["election_id"]
    resp_all = client.get("/election", headers=auth_headers(admin_token))
    assert resp_all.status_code == 200
    all_elections = resp_all.json()
    assert any(e.get("election_id") == election_id for e in all_elections)


def test_retrieve_specific_election(admin_token, client):
    resp = create_election(client, token=admin_token)
    election_id = resp.json()["election_id"]
    resp_one = client.get(f"/election/{election_id}", headers=auth_headers(admin_token))
    assert resp_one.status_code == 200
    e = resp_one.json()
    assert e.get("election_id") == election_id
    assert isinstance(e.get("posts"), list)


def test_add_post_to_election(admin_token, client, admin_post, member_post):
    resp = create_election(client, token=admin_token, post_ids=[admin_post.id, member_post.id])
    response = resp.json()
    assert resp.status_code in (200, 201), resp.text
    assert "posts" in response
    assert len(response["posts"]) == 2
    assert all(post.get("id") in (admin_post.id, member_post.id) for post in response["posts"])


def test_remove_post_from_election(admin_token, client, admin_post, member_post):
    resp = create_election(client, token=admin_token, post_ids=[admin_post.id, member_post.id])
    election_id = resp.json()["election_id"]
    resp_remove = patch_election(client, election_id, token=admin_token, post_ids=[admin_post.id])
    assert resp_remove.status_code in (200, 204), resp_remove.text
    assert "posts" in resp_remove.json()
    assert len(resp_remove.json()["posts"]) == 1
    assert resp_remove.json()["posts"][0].get("id") == admin_post.id


def test_member_create_candidation(admin_token, member_token, client, admin_post):
    resp = create_election(client, token=admin_token, post_ids=[admin_post.id])
    election_id = resp.json()["election_id"]
    resp_cand = client.post(f"/candidate/{election_id}?post_id={admin_post.id}", headers=auth_headers(member_token))
    assert resp_cand.status_code in (200, 201), resp_cand.text


def test_member_retrieve_my_candidations(admin_token, member_token, client, admin_post):
    resp = create_election(client, token=admin_token)
    election_id = resp.json()["election_id"]
    client.post(
        f"/election/{election_id}", json={"posts": [{"post_id": admin_post.id}]}, headers=auth_headers(admin_token)
    )
    client.post(f"/candidate/{election_id}?post_id={admin_post.id}", headers=auth_headers(member_token))
    resp_my = client.get(f"/election/my-candidations/{election_id}", headers=auth_headers(member_token))
    assert resp_my.status_code == 200
    assert resp_my.json() is not None


def test_member_many_candidations_duplicate_rejected(admin_token, member_token, client, admin_post):
    resp = create_election(client, token=admin_token)
    election_id = resp.json()["election_id"]
    client.post(
        f"/election/{election_id}", json={"posts": [{"post_id": admin_post.id}]}, headers=auth_headers(admin_token)
    )
    client.post(f"/candidate/{election_id}?post_id={admin_post.id}", headers=auth_headers(member_token))
    resp_many = client.post(
        f"/candidate/many/{election_id}", json={"post_ids": [admin_post.id]}, headers=auth_headers(member_token)
    )
    assert (
        resp_many.status_code == 400
    ), f"Expected 400 when re-adding same candidation, got {resp_many.status_code}: {resp_many.text}"
