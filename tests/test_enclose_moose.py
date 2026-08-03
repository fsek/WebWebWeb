# type: ignore
import pytest
from .basic_factories import auth_headers
from datetime import datetime, UTC, timedelta


def create_level(client, token, **kwargs):
    default_data = {"level_id": "test_level", "name": "test", "encoded_grid": ".~.\n.H.\n~.~", "wall_budget": 4}
    return client.post("/enclose-moose/admin/levels", json=default_data | kwargs, headers=auth_headers(token))


def patch_level(client, token, level_id, **kwargs):
    return client.patch(f"/enclose-moose/admin/levels/{level_id}", json=kwargs, headers=auth_headers(token))


def delete_level(client, token, level_id):
    return client.delete(f"/enclose-moose/admin/levels/{level_id}", headers=auth_headers(token))


def admin_get_level(client, token, level_id):
    return client.get(f"/enclose-moose/admin/levels/{level_id}", headers=auth_headers(token))


def get_level(client, token, level_id):
    return client.get(f"/enclose-moose/levels/{level_id}", headers=auth_headers(token))


def admin_get_all_levels(client, token):
    return client.get("/enclose-moose/admin/levels", headers=auth_headers(token))


def get_all_levels(client, token):
    return client.get("/enclose-moose/levels", headers=auth_headers(token))


def submit_solution(client, token, level_id, player_solution, secret_header="happy_secret_key"):
    headers = auth_headers(token)
    if secret_header is not None:
        headers["enclose-moose-token"] = secret_header

    body = {"player_solution": player_solution}
    return client.post(f"/enclose-moose/submissions/{level_id}", json=body, headers=headers)


def get_submission(client, token, level_id):
    return client.get(f"/enclose-moose/submissions/{level_id}", headers=auth_headers(token))


def admin_get_all_submissions(client, token):
    return client.get("/enclose-moose/admin/submissions", headers=auth_headers(token))


def get_all_submissions(client, token):
    return client.get("/enclose-moose/submissions", headers=auth_headers(token))


def test_admin_manage_level(client, admin_token):
    res_create_invalid = create_level(client, admin_token, encoded_grid=".~.")
    assert res_create_invalid.status_code == 400

    res_create_unsolvable = create_level(client, admin_token, wall_budget=1)
    assert res_create_unsolvable.status_code == 400

    res_create = create_level(client, admin_token, level_id="released_test")
    assert res_create.status_code == 200

    res_get = admin_get_level(client, admin_token, "released_test")
    assert res_get.status_code == 200

    res_get_all = admin_get_all_levels(client, admin_token)
    assert res_get_all.status_code == 200

    res_patch = patch_level(client, admin_token, "released_test", name="updated_name")
    assert res_patch.status_code == 200
    assert res_patch.json()["name"] == "updated_name"

    res_delete = delete_level(client, admin_token, "released_test")
    assert res_delete.status_code == 200

    res_get = admin_get_level(client, admin_token, "released_test")
    assert res_get.status_code == 404

    res_get_submissions = admin_get_all_submissions(client, admin_token)
    assert res_get_submissions.status_code == 200


def test_admin_duplicate_level(
    client, admin_token
):  # Has to be a seperate test because the 409 (IntegrityError) otherwise expires the session state (problematic because it uses the same session for every request, unlike prod)
    create_level(client, admin_token, level_id="released_test")

    res_create_duplicate = create_level(client, admin_token, level_id="released_test")
    assert res_create_duplicate.status_code == 409


def test_member_cannot_access_admin_routes(client, member_token, admin_token):
    res_create = create_level(client, member_token, level_id="released_test")
    assert res_create.status_code == 403

    create_level(client, admin_token, level_id="released_test")

    res_admin_get = admin_get_level(client, member_token, "released_test")
    assert res_admin_get.status_code == 403

    res_admin_get_all = admin_get_all_levels(client, member_token)
    assert res_admin_get_all.status_code == 403

    res_patch = patch_level(client, member_token, "released_test", name="updated_name")
    assert res_patch.status_code == 403
    res_patch_get = get_level(client, member_token, "released_test")
    assert res_patch_get.json()["name"] != "updated_name"

    res_del = delete_level(client, member_token, "released_test")
    assert res_del.status_code == 403

    res_del_get = get_level(client, member_token, "released_test")
    assert res_del_get.status_code == 200

    res_submissions = admin_get_all_submissions(client, member_token)
    assert res_submissions.status_code == 403


def test_levels(client, member_token, admin_token):
    future_date = (datetime.now(UTC).date() + timedelta(days=2)).isoformat()
    create_level(client, admin_token, level_id="unreleased_test", release_date=future_date)
    create_level(client, admin_token, level_id="released_test")

    res_get_admin_unreleased = admin_get_level(client, admin_token, "unreleased_test")
    assert res_get_admin_unreleased.status_code == 200

    res_get_admin_released = admin_get_level(client, admin_token, "released_test")
    assert res_get_admin_released.status_code == 200

    res_get_member_unreleased = get_level(client, member_token, "unreleased_test")
    assert res_get_member_unreleased.status_code == 404

    res_get_member_released = get_level(client, member_token, "released_test")
    assert res_get_member_released.status_code == 200

    res_admin_get_all = admin_get_all_levels(client, admin_token)
    assert res_admin_get_all.status_code == 200
    assert len(res_admin_get_all.json()) == 2

    res_get_all_member = get_all_levels(client, member_token)
    assert res_get_all_member.status_code == 200
    assert len(res_get_all_member.json()) == 1


def test_submission(client, member_token, admin_token):
    res_non_existent = submit_solution(client, member_token, "released_test", player_solution=[3, 5, 7])
    assert res_non_existent.status_code == 404

    res_get_non_existent = get_submission(client, member_token, "released_test")
    assert res_get_non_existent.status_code == 404

    create_level(client, admin_token, level_id="released_test")
    res_member = submit_solution(client, member_token, "released_test", player_solution=[3, 5, 7])
    assert res_member.status_code == 200

    res_member_invalid = submit_solution(client, member_token, "released_test", player_solution=[3, 5])
    assert res_member_invalid.status_code == 400

    res_invalid_token = submit_solution(
        client, member_token, "released_test", player_solution=[3, 5, 7], secret_header="I love tests!"
    )
    assert res_invalid_token.status_code == 401

    res_get = get_submission(client, member_token, "released_test")
    assert res_get.status_code == 200

    future_date = (datetime.now(UTC).date() + timedelta(days=2)).isoformat()
    create_level(client, admin_token, level_id="unreleased_test", release_date=future_date)
    res_unreleased = submit_solution(client, member_token, "unreleased_test", player_solution=[3, 5, 7])
    assert res_unreleased.status_code == 404

    submit_solution(client, admin_token, "released_test", player_solution=[3, 5, 7])
    res_get_all = get_all_submissions(client, member_token)
    assert res_get_all.status_code == 200
    assert len(res_get_all.json()) == 1


def test_submissions_clear(client, member_token, admin_token):
    create_level(client, admin_token, level_id="released_test")
    submit_solution(client, member_token, "released_test", player_solution=[3, 5, 7])

    patch_level(client, admin_token, "released_test", name="updated_name")
    res_get_unchanged = get_submission(client, member_token, "released_test")
    assert res_get_unchanged.status_code == 200

    patch_level(client, admin_token, "released_test", wall_budget=10)
    res_get_changed = get_submission(client, member_token, "released_test")
    assert res_get_changed.status_code == 404

    submit_solution(client, member_token, "released_test", player_solution=[3, 5, 7])
    delete_level(client, admin_token, "released_test")
    res_get_deleted = get_submission(client, member_token, "released_test")
    assert res_get_deleted.status_code == 404


def test_non_member_cannot_access_member_routes(client, non_member_token, admin_token):
    create_level(client, admin_token, level_id="released_test")

    res_get = get_level(client, non_member_token, "released_test")
    assert res_get.status_code == 403

    res_get_all = get_all_levels(client, non_member_token)
    assert res_get_all.status_code == 403

    res_submit = submit_solution(client, non_member_token, "released_test", player_solution=[3, 5, 7])
    assert res_submit.status_code == 403

    res_get_submission = submit_solution(client, non_member_token, "released_test", player_solution=[3, 5, 7])
    assert res_get_submission.status_code == 403

    res_get_all_submissions = get_all_submissions(client, non_member_token)
    assert res_get_all_submissions.status_code == 403
