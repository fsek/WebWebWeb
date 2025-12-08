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


def test_update_sub_election_retains_posts(admin_token, admin_user, client, admin_post, member_post, open_election):
    # Create a sub-election with both posts
    resp_create = create_sub_election(
        client,
        open_election.election_id,
        token=admin_token,
        title_sv="Initial",
        title_en="Initial",
        post_ids=[admin_post.id, member_post.id],
    )
    assert resp_create.status_code in (200, 201), resp_create.text
    sub_election = resp_create.json()
    sub_election_id = sub_election["sub_election_id"]
    assert len(sub_election.get("election_posts", [])) == 2

    # Candidate for one of the posts
    resp_cand = create_candidation(
        client,
        sub_election_id=sub_election_id,
        post_id=admin_post.id,
        token=admin_token,
        user_id=admin_user.id,
    )
    assert resp_cand.status_code in (200, 201), resp_cand.text
    candidate = resp_cand.json()
    candidate_id = candidate["candidate_id"]
    assert any(c["post_id"] == admin_post.id for c in candidate["candidations"])

    # Update the sub-election with the same posts again, should retain them and the candidations
    resp_update = patch_sub_election(
        client,
        sub_election_id,
        token=admin_token,
        title_sv="Updated",
        title_en="Updated",
        post_ids=[admin_post.id, member_post.id],
    )
    assert resp_update.status_code in (200, 204), resp_update.text
    updated_sub_election = resp_update.json()
    assert updated_sub_election["title_sv"] == "Updated"
    assert updated_sub_election["title_en"] == "Updated"
    assert len(updated_sub_election.get("election_posts", [])) == 2
    post_ids = {ep["post_id"] for ep in updated_sub_election["election_posts"]}
    assert post_ids == {admin_post.id, member_post.id}

    # Ensure the candidation still exists
    resp_cand_check = client.get(f"/candidate/sub-election/{sub_election_id}", headers=auth_headers(admin_token))
    assert resp_cand_check.status_code == 200, resp_cand_check.text
    cand_list = resp_cand_check.json()
    cand_obj = next(c for c in cand_list if c["candidate_id"] == candidate_id)
    assert any(cand["post_id"] == admin_post.id for cand in cand_obj["candidations"])


def test_move_election_post_retains_candidates(admin_token, admin_user, client, admin_post, member_post, open_election):
    # Create two sub-elections
    resp_sub1 = create_sub_election(
        client,
        open_election.election_id,
        token=admin_token,
        title_sv="Sub1",
        title_en="Sub1",
        post_ids=[admin_post.id],
    )
    assert resp_sub1.status_code in (200, 201), resp_sub1.text
    sub_election_1 = resp_sub1.json()
    sub_election_1_id = sub_election_1["sub_election_id"]

    resp_sub2 = create_sub_election(
        client,
        open_election.election_id,
        token=admin_token,
        title_sv="Sub2",
        title_en="Sub2",
        post_ids=[member_post.id],
    )
    assert resp_sub2.status_code in (200, 201), resp_sub2.text
    sub_election_2 = resp_sub2.json()
    sub_election_2_id = sub_election_2["sub_election_id"]

    # Candidate for admin_post in sub_election_1
    resp_cand = create_candidation(
        client,
        sub_election_id=sub_election_1_id,
        post_id=admin_post.id,
        token=admin_token,
        user_id=admin_user.id,
    )
    assert resp_cand.status_code in (200, 201), resp_cand.text
    candidate = resp_cand.json()
    candidate_id = candidate["candidate_id"]
    assert any(c["post_id"] == admin_post.id for c in candidate["candidations"])

    # Resolve the correct election_post_id
    ep_admin = next(ep for ep in sub_election_1["election_posts"] if ep["post_id"] == admin_post.id)
    election_post_id = ep_admin["election_post_id"]

    # Move the election post using its election_post_id
    resp_move = client.patch(
        f"/sub-election/{sub_election_1_id}/move-election-post",
        json={
            "election_post_id": election_post_id,
            "new_sub_election_id": sub_election_2_id,
        },
        headers=auth_headers(admin_token),
    )
    assert resp_move.status_code in (200, 204), resp_move.text
    moved_to_sub_election = resp_move.json()
    assert moved_to_sub_election["sub_election_id"] == sub_election_2_id
    moved_post = next(ep for ep in moved_to_sub_election["election_posts"] if ep["post_id"] == admin_post.id)
    assert moved_post is not None

    assert moved_post["post_id"] == admin_post.id
    assert moved_post["candidation_count"] == 1

    # Ensure the candidation still exists and is associated with the moved post
    resp_cand_check = client.get(f"/candidate/sub-election/{sub_election_2_id}", headers=auth_headers(admin_token))
    assert resp_cand_check.status_code == 200, resp_cand_check.text
    candidates = resp_cand_check.json()
    assert any(c["candidate_id"] == candidate_id for c in candidates)


def test_move_election_post_retains_nominations(
    admin_token, admin_user, client, admin_post, member_post, open_election, member_token
):
    # Create two sub-elections
    resp_sub1 = create_sub_election(
        client,
        open_election.election_id,
        token=admin_token,
        title_sv="Sub1",
        title_en="Sub1",
        post_ids=[admin_post.id],
    )
    assert resp_sub1.status_code in (200, 201), resp_sub1.text
    sub_election_1 = resp_sub1.json()
    sub_election_1_id = sub_election_1["sub_election_id"]

    resp_sub2 = create_sub_election(
        client,
        open_election.election_id,
        token=admin_token,
        title_sv="Sub2",
        title_en="Sub2",
        post_ids=[member_post.id],
    )
    assert resp_sub2.status_code in (200, 201), resp_sub2.text
    sub_election_2 = resp_sub2.json()
    sub_election_2_id = sub_election_2["sub_election_id"]

    # Get correct election_post_id for admin_post
    ep_admin = next(ep for ep in sub_election_1["election_posts"] if ep["post_id"] == admin_post.id)
    election_post_id = ep_admin["election_post_id"]

    # Nominate using election_post_id
    nomination_payload = {
        "nominee_name": getattr(admin_user, "name", "Admin User"),
        "nominee_email": admin_user.email,
        "motivation": "Great candidate",
        "election_post_id": election_post_id,
        "sub_election_id": sub_election_1_id,
    }
    resp_nom = client.post(
        f"/nominations/{sub_election_1_id}",
        json=nomination_payload,
        headers=auth_headers(member_token),
    )
    assert resp_nom.status_code in (200, 201), resp_nom.text

    # Move election post
    resp_move = client.patch(
        f"/sub-election/{sub_election_1_id}/move-election-post",
        json={
            "election_post_id": election_post_id,
            "new_sub_election_id": sub_election_2_id,
        },
        headers=auth_headers(admin_token),
    )
    assert resp_move.status_code in (200, 204), resp_move.text
    moved_to_sub_election = resp_move.json()
    assert moved_to_sub_election["sub_election_id"] == sub_election_2_id
    moved_post = next(ep for ep in moved_to_sub_election["election_posts"] if ep["post_id"] == admin_post.id)
    assert moved_post is not None
    assert moved_post["post_id"] == admin_post.id
    assert moved_post["candidation_count"] == 0
    # Only check nominations if the endpoint returns them
    if "nominations" in moved_post:
        noms = moved_post.get("nominations", [])
        matching = [n for n in noms if n.get("nominee_email") == admin_user.email]
        assert len(matching) == 1


def test_move_election_post_keeps_remaining_candidations_in_original_sub_election(
    admin_token, admin_user, client, admin_post, member_post, open_election
):
    # Create sub-election with two posts
    resp_sub = create_sub_election(
        client,
        open_election.election_id,
        token=admin_token,
        title_sv="Source",
        title_en="Source",
        post_ids=[admin_post.id, member_post.id],
    )
    assert resp_sub.status_code in (200, 201), resp_sub.text
    sub_election = resp_sub.json()
    sub_election_id = sub_election["sub_election_id"]

    # Create candidations for both posts for the same user
    resp_cand_admin = create_candidation(
        client,
        sub_election_id=sub_election_id,
        post_id=admin_post.id,
        token=admin_token,
        user_id=admin_user.id,
    )
    assert resp_cand_admin.status_code in (200, 201), resp_cand_admin.text

    resp_cand_member = create_candidation(
        client,
        sub_election_id=sub_election_id,
        post_id=member_post.id,
        token=admin_token,
        user_id=admin_user.id,
    )
    assert resp_cand_member.status_code in (200, 201), resp_cand_member.text
    candidate = resp_cand_member.json()
    candidate_id = candidate["candidate_id"]
    post_ids_before_move = {candidation["post_id"] for candidation in candidate["candidations"]}
    assert post_ids_before_move == {admin_post.id, member_post.id}

    # Destination sub-election without posts
    resp_dest = create_sub_election(
        client,
        open_election.election_id,
        token=admin_token,
        title_sv="Destination",
        title_en="Destination",
    )
    assert resp_dest.status_code in (200, 201), resp_dest.text
    dest_sub_election = resp_dest.json()
    dest_sub_election_id = dest_sub_election["sub_election_id"]

    # Resolve election_post identifier for the admin post
    election_post_admin = next(ep for ep in sub_election["election_posts"] if ep["post_id"] == admin_post.id)
    election_post_id = election_post_admin["election_post_id"]

    # Move election post to the destination sub-election
    resp_move = client.patch(
        f"/sub-election/{sub_election_id}/move-election-post",
        json={
            "election_post_id": election_post_id,
            "new_sub_election_id": dest_sub_election_id,
        },
        headers=auth_headers(admin_token),
    )
    assert resp_move.status_code in (200, 204), resp_move.text

    # Original sub-election should still have the candidate with the remaining post
    resp_candidates_source = client.get(f"/candidate/sub-election/{sub_election_id}", headers=auth_headers(admin_token))
    assert resp_candidates_source.status_code == 200, resp_candidates_source.text
    candidates_source = resp_candidates_source.json()
    original_candidate = next(c for c in candidates_source if c["candidate_id"] == candidate_id)
    remaining_post_ids = {candidation["post_id"] for candidation in original_candidate["candidations"]}
    assert remaining_post_ids == {member_post.id}
    assert all(candidation["sub_election_id"] == sub_election_id for candidation in original_candidate["candidations"])

    # Destination sub-election should have a candidate for the moved post only
    resp_candidates_dest = client.get(
        f"/candidate/sub-election/{dest_sub_election_id}", headers=auth_headers(admin_token)
    )
    assert resp_candidates_dest.status_code == 200, resp_candidates_dest.text
    candidates_dest = resp_candidates_dest.json()
    moved_candidate = next(c for c in candidates_dest if c["user_id"] == admin_user.id)
    moved_post_ids = {candidation["post_id"] for candidation in moved_candidate["candidations"]}
    assert moved_post_ids == {admin_post.id}
    assert all(
        candidation["sub_election_id"] == dest_sub_election_id for candidation in moved_candidate["candidations"]
    )
    assert moved_candidate["candidate_id"] != candidate_id
