# type: ignore
from .basic_factories import (
    create_election,
    auth_headers,
    patch_election,
    create_candidation,
    create_sub_election,
    patch_sub_election,
)
from datetime import datetime, timedelta, timezone


def test_create_election(admin_token, client):
    resp = create_election(client, token=admin_token)
    assert resp.status_code in (200, 201), f"Create election failed: {resp.text}"
    election = resp.json()
    assert "election_id" in election


def test_retrieve_all_elections(admin_token, client, open_election):
    election_id = open_election.election_id
    resp_all = client.get("/election", headers=auth_headers(admin_token))
    assert resp_all.status_code == 200
    all_elections = resp_all.json()
    assert any(e.get("election_id") == election_id for e in all_elections)


def test_retrieve_specific_election(admin_token, client, open_election):
    election_id = open_election.election_id
    resp_one = client.get(f"/election/{election_id}", headers=auth_headers(admin_token))
    assert resp_one.status_code == 200
    e = resp_one.json()
    assert e.get("election_id") == election_id
    assert isinstance(e.get("sub_elections"), list)


def test_add_sub_election(admin_token, client, open_election):
    election_id = open_election.election_id
    sub_election_data = {
        "title_sv": "UnderVal",
        "title_en": "SubElection",
    }
    resp_sub = create_sub_election(client, election_id, token=admin_token, **sub_election_data)
    assert resp_sub.status_code in (200, 201), resp_sub.text
    sub_election = resp_sub.json()
    assert sub_election.get("title_sv") == sub_election_data["title_sv"]
    assert sub_election.get("title_en") == sub_election_data["title_en"]
    assert "sub_election_id" in sub_election


def test_add_post_to_sub_election(admin_token, client, admin_post, member_post, open_election):
    resp = create_sub_election(
        client, open_election.election_id, token=admin_token, post_ids=[admin_post.id, member_post.id]
    )
    response = resp.json()
    assert resp.status_code in (200, 201), resp.text
    assert "election_posts" in response
    assert len(response["election_posts"]) == 2
    assert all(ep.get("post_id") in (admin_post.id, member_post.id) for ep in response["election_posts"])


def test_remove_post_from_election(admin_token, client, admin_post, open_sub_election):
    # Should have admin_post and member_post initially
    assert len(open_sub_election.posts) == 2
    resp_remove = patch_sub_election(
        client, open_sub_election.sub_election_id, token=admin_token, post_ids=[admin_post.id]
    )
    assert resp_remove.status_code in (200, 204), resp_remove.text
    assert "election_posts" in resp_remove.json()
    assert len(resp_remove.json()["election_posts"]) == 1
    assert resp_remove.json()["election_posts"][0].get("post_id") == admin_post.id


def test_member_create_candidation(member_token, client, admin_post, membered_user, open_sub_election):
    resp_cand = client.post(
        f"/candidate/{open_sub_election.sub_election_id}?post_id={admin_post.id}&user_id={membered_user.id}",
        headers=auth_headers(member_token),
    )
    assert resp_cand.status_code in (200, 201), resp_cand.text
    assert resp_cand.json().get("user_id") == membered_user.id


def test_member_retrieve_my_candidations(
    member_token, client, admin_post, membered_user, open_sub_election, open_election
):
    resp = create_candidation(client, open_sub_election.sub_election_id, admin_post.id, member_token, membered_user.id)
    assert resp.status_code in (200, 201), resp.text
    resp_my = client.get(f"/candidate/my-candidations/{open_election.election_id}", headers=auth_headers(member_token))
    assert resp_my.status_code == 200
    my_candidations = resp_my.json()
    assert any(c.get("post_id") == admin_post.id for c in my_candidations)


def test_delete_election(admin_token, client, open_election):
    election_id = open_election.election_id
    resp_del = client.delete(f"/election/{election_id}", headers=auth_headers(admin_token))
    assert resp_del.status_code == 200
    # Should not be found after deletion
    resp_get = client.get(f"/election/{election_id}", headers=auth_headers(admin_token))
    assert resp_get.status_code == 404


def test_only_admin_can_edit_election(admin_token, member_token, non_member_token, client, admin_post, open_election):
    election_id = open_election.election_id

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


def test_election_visibility_all_roles(admin_token, member_token, non_member_token, client, admin_post, open_election):
    election_id = open_election.election_id

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


def test_admin_can_list_candidates(admin_token, member_token, client, admin_post, membered_user, open_sub_election):
    resp_cand = create_candidation(
        client,
        sub_election_id=open_sub_election.sub_election_id,
        post_id=admin_post.id,
        token=member_token,
        user_id=membered_user.id,
    )
    assert resp_cand.status_code in (200, 201), resp_cand.text

    resp_election = client.get(
        f"/candidate/election/{open_sub_election.election_id}", headers=auth_headers(admin_token)
    )
    assert resp_election.status_code == 200, resp_election.text
    candidates_election = resp_election.json()
    assert any(c.get("user_id") == membered_user.id for c in candidates_election)

    resp_sub = client.get(
        f"/candidate/sub-election/{open_sub_election.sub_election_id}", headers=auth_headers(admin_token)
    )
    assert resp_sub.status_code == 200, resp_sub.text
    candidates_sub = resp_sub.json()
    assert any(c.get("user_id") == membered_user.id for c in candidates_sub)

    assert candidates_election == candidates_sub


def test_member_create_candidation_for_self_and_duplicate_rejected(
    member_token, client, admin_post, membered_user, open_sub_election
):
    sub_election_id = open_sub_election.sub_election_id

    first = create_candidation(
        client, sub_election_id=sub_election_id, post_id=admin_post.id, token=member_token, user_id=membered_user.id
    )
    assert first.status_code in (200, 201), first.text

    dup = create_candidation(
        client, sub_election_id=sub_election_id, post_id=admin_post.id, token=member_token, user_id=membered_user.id
    )
    assert dup.status_code in (400, 409), dup.text


def test_get_my_candidations_lists_expected_posts(member_token, client, admin_post, membered_user, open_sub_election):
    sub_election_id = open_sub_election.sub_election_id

    created = create_candidation(
        client, sub_election_id=sub_election_id, post_id=admin_post.id, token=member_token, user_id=membered_user.id
    )
    assert created.status_code in (200, 201), created.text

    my_resp = client.get(
        f"/candidate/my-candidations/{open_sub_election.election_id}", headers=auth_headers(member_token)
    )
    assert my_resp.status_code == 200, my_resp.text
    my = my_resp.json()
    assert any(item.get("post_id") == admin_post.id for item in my)


def test_member_can_delete_own_candidation_and_non_member_forbidden(
    member_token, non_member_token, client, admin_post, membered_user, open_sub_election
):
    created = create_candidation(
        client,
        sub_election_id=open_sub_election.sub_election_id,
        post_id=admin_post.id,
        token=member_token,
        user_id=membered_user.id,
    )
    assert created.status_code in (200, 201), created.text

    my = client.get(
        f"/candidate/my-candidations/{open_sub_election.election_id}", headers=auth_headers(member_token)
    ).json()
    ep_id = next(item["election_post_id"] for item in my if item["post_id"] == admin_post.id)

    # Member deletes own candidation
    del_self = client.delete(
        f"/candidate/?election_post_id={ep_id}&candidate_id={created.json()['candidate_id']}",
        headers=auth_headers(member_token),
    )
    assert del_self.status_code == 204, del_self.text

    # Recreate candidation, then non-member tries to delete -> forbidden
    created2 = create_candidation(
        client,
        sub_election_id=open_sub_election.sub_election_id,
        post_id=admin_post.id,
        token=member_token,
        user_id=membered_user.id,
    )
    assert created2.status_code in (200, 201), created2.text
    my2 = client.get(
        f"/candidate/my-candidations/{open_sub_election.election_id}", headers=auth_headers(member_token)
    ).json()
    ep_id2 = next(item["election_post_id"] for item in my2 if item["post_id"] == admin_post.id)

    del_non_member = client.delete(
        f"/candidate/?election_post_id={ep_id2}&candidate_id={membered_user.id}",
        headers=auth_headers(non_member_token),
    )
    assert del_non_member.status_code == 403, del_non_member.text


def test_admin_can_delete_candidate(admin_token, member_token, client, admin_post, membered_user, open_sub_election):

    created = create_candidation(
        client,
        sub_election_id=open_sub_election.sub_election_id,
        post_id=admin_post.id,
        token=member_token,
        user_id=membered_user.id,
    )
    assert created.status_code in (200, 201), created.text

    resp_del = client.delete(
        f"/candidate/{open_sub_election.sub_election_id}/candidate/{membered_user.id}",
        headers=auth_headers(admin_token),
    )
    assert resp_del.status_code == 204, resp_del.text

    cand_list = client.get(
        f"/candidate/election/{open_sub_election.election_id}", headers=auth_headers(admin_token)
    ).json()
    assert not any(c.get("user_id") == membered_user.id for c in cand_list)


def test_populate_election_admin_can_populate_and_creates_subelections(admin_token, client, open_election):
    now = datetime.now(timezone.utc)
    payload = {
        "semester": "HT",
        "end_time_guild": (now + timedelta(days=5)).isoformat(),
        "end_time_board": (now + timedelta(days=4)).isoformat(),
        "end_time_board_intermediate": (now + timedelta(days=3)).isoformat(),
        "end_time_educational_council": (now + timedelta(days=2)).isoformat(),
    }
    resp = client.post(
        f"/election/{open_election.election_id}/populate",
        json=payload,
        headers=auth_headers(admin_token),
    )
    assert resp.status_code in (200, 201), resp.text
    data = resp.json()
    assert "sub_elections" in data
    assert isinstance(data["sub_elections"], list)
    assert len(data["sub_elections"]) > 0


def test_populate_election_member_and_non_member_forbidden(member_token, non_member_token, client, open_election):
    now = datetime.now(timezone.utc)
    payload = {
        "semester": "HT",
        "end_time_guild": (now + timedelta(days=5)).isoformat(),
        "end_time_board": (now + timedelta(days=4)).isoformat(),
        "end_time_board_intermediate": (now + timedelta(days=3)).isoformat(),
        "end_time_educational_council": (now + timedelta(days=2)).isoformat(),
    }

    resp_member = client.post(
        f"/election/{open_election.election_id}/populate", json=payload, headers=auth_headers(member_token)
    )
    assert resp_member.status_code == 403, resp_member.text

    resp_non_member = client.post(
        f"/election/{open_election.election_id}/populate",
        json=payload,
        headers=auth_headers(non_member_token),
    )
    assert resp_non_member.status_code == 403, resp_non_member.text
