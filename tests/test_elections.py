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


def test_delete_election(admin_token, client):
    resp = create_election(client, token=admin_token)
    election_id = resp.json()["election_id"]
    resp_del = client.delete(f"/election/{election_id}", headers=auth_headers(admin_token))
    assert resp_del.status_code == 200
    # Should not be found after deletion
    resp_get = client.get(f"/election/{election_id}", headers=auth_headers(admin_token))
    assert resp_get.status_code == 404


def test_only_admin_can_edit_election(admin_token, member_token, non_member_token, client, admin_post):
    # Create election as admin
    resp = create_election(client, token=admin_token, post_ids=[admin_post.id])
    election_id = resp.json()["election_id"]

    # Admin can PATCH
    patch_resp = patch_election(
        client,
        election_id=election_id,
        title_sv="NewTitle",
        token=admin_token,
    )
    assert patch_resp.status_code in (200, 204)

    # Member cannot PATCH
    patch_resp_member = patch_election(
        client,
        election_id=election_id,
        title_sv="ShouldFail",
        token=member_token,
    )
    assert patch_resp_member.status_code == 403

    # Non-member cannot PATCH
    patch_resp_non_member = patch_election(
        client,
        election_id=election_id,
        title_sv="ShouldFail",
        token=non_member_token,
    )
    assert patch_resp_non_member.status_code == 403

    # Admin can DELETE
    del_resp = client.delete(f"/election/{election_id}", headers=auth_headers(admin_token))
    assert del_resp.status_code == 200

    # Member cannot DELETE
    resp = create_election(client, token=admin_token, post_ids=[admin_post.id])
    election_id = resp.json()["election_id"]
    del_resp_member = client.delete(f"/election/{election_id}", headers=auth_headers(member_token))
    assert del_resp_member.status_code == 403

    # Non-member cannot DELETE
    del_resp_non_member = client.delete(f"/election/{election_id}", headers=auth_headers(non_member_token))
    assert del_resp_non_member.status_code == 403


def test_election_visibility_all_roles(admin_token, member_token, non_member_token, client, admin_post):
    # Create election as admin
    resp = create_election(client, token=admin_token, post_ids=[admin_post.id])
    election_id = resp.json()["election_id"]

    # Admin can see all elections (GET /election)
    resp_admin = client.get("/election", headers=auth_headers(admin_token))
    assert resp_admin.status_code == 200
    assert any(e.get("election_id") == election_id for e in resp_admin.json())

    # Member cannot access /election (should be 403)
    resp_member = client.get("/election", headers=auth_headers(member_token))
    assert resp_member.status_code == 403

    # Non-member cannot access /election (should be 403)
    resp_non_member = client.get("/election", headers=auth_headers(non_member_token))
    assert resp_non_member.status_code == 403

    # Admin can see specific election (GET /election/{id})
    resp_admin_one = client.get(f"/election/{election_id}", headers=auth_headers(admin_token))
    assert resp_admin_one.status_code == 200
    assert resp_admin_one.json().get("election_id") == election_id

    # Member cannot access /election/{id} (should be 403)
    resp_member_one = client.get(f"/election/{election_id}", headers=auth_headers(member_token))
    assert resp_member_one.status_code == 403

    # Non-member cannot access /election/{id} (should be 403)
    resp_non_member_one = client.get(f"/election/{election_id}", headers=auth_headers(non_member_token))
    assert resp_non_member_one.status_code == 403

    # Member can see all elections (GET /election/member/)
    resp_member_list = client.get("/election/member/", headers=auth_headers(member_token))
    assert resp_member_list.status_code == 200
    assert any(e.get("election_id") == election_id for e in resp_member_list.json())

    # Non-member cannot access /election/member/ (should be 403)
    resp_non_member_member = client.get("/election/member/", headers=auth_headers(non_member_token))
    assert resp_non_member_member.status_code == 403

    # Member can see specific election (GET /election/member/{id})
    resp_member_one_member = client.get(f"/election/member/{election_id}", headers=auth_headers(member_token))
    assert resp_member_one_member.status_code == 200
    assert resp_member_one_member.json().get("election_id") == election_id

    # Non-member cannot access /election/member/{id} (should be 403)
    resp_non_member_one_member = client.get(f"/election/member/{election_id}", headers=auth_headers(non_member_token))
    assert resp_non_member_one_member.status_code == 403
