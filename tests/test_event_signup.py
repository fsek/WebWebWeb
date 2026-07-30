# type: ignore
import pytest
from .basic_factories import add_user_to_group, auth_headers, event_data_factory


def test_signup_with_allowed_group_type(client, member_token, membered_user, nollning_event, mentor_group):
    """A group whose type is in mentor_group_types is accepted."""
    response = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mentor_group.name},
        headers=auth_headers(member_token),
    )

    assert response.status_code in (200, 201), response.text
    assert response.json()["group_name"] == mentor_group.name


def test_signup_with_disallowed_group_type(client, member_token, membered_user, nollning_event, mission_group):
    """A group whose type is not in mentor_group_types is rejected."""
    response = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mission_group.name},
        headers=auth_headers(member_token),
    )

    assert response.status_code == 403


def test_signup_with_group_the_user_is_not_in(client, member_token, membered_user, nollning_event, mentor_group):
    """A group name the user isn't a member of is rejected, even if the type is allowed."""
    response = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": "Något helt annat"},
        headers=auth_headers(member_token),
    )

    assert response.status_code == 403


def test_signup_without_group(client, member_token, membered_user, nollning_event, mission_group):
    """Signing up without picking a group is not restricted by the group types."""
    response = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id},
        headers=auth_headers(member_token),
    )

    assert response.status_code in (200, 201), response.text
    assert response.json()["group_name"] is None


def test_admin_can_sign_up_user_with_disallowed_group(
    client, admin_token, membered_user, nollning_event, mission_group
):
    """Someone who may manage events is not restricted by the group types."""
    response = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mission_group.name},
        headers=auth_headers(admin_token),
    )

    assert response.status_code in (200, 201), response.text
    assert response.json()["group_name"] == mission_group.name


@pytest.mark.parametrize("allow_other_mentors", [True, False])
def test_signup_as_mentor_of_group_with_other_type(
    client,
    admin_token,
    admin_council_id,
    member_token,
    membered_user,
    db_session,
    allow_other_mentors,
):
    """A mentor may sign up with a group of a disallowed type only if the event allows it."""
    group = add_user_to_group(db_session, membered_user, "Uppdraget", "Mission", "Mentor")
    data = event_data_factory(
        council_id=admin_council_id,
        is_nollning_event=True,
        mentor_group_types=["Mentor"],
        allow_other_mentors=allow_other_mentors,
    )
    event = client.post("/events/", json=data, headers=auth_headers(admin_token)).json()

    response = client.post(
        f"/event-signup/{event['id']}",
        json={"user_id": membered_user.id, "group_name": group.name},
        headers=auth_headers(member_token),
    )

    if allow_other_mentors:
        assert response.status_code in (200, 201), response.text
    else:
        assert response.status_code == 403


def test_non_nollning_event_ignores_group_types(client, member_token, membered_user, event, mission_group):
    """Group types only restrict nollning events."""
    response = client.post(
        f"/event-signup/{event['id']}",
        json={"user_id": membered_user.id, "group_name": mission_group.name},
        headers=auth_headers(member_token),
    )

    assert response.status_code in (200, 201), response.text


def test_update_signup_without_group_name_is_allowed(client, member_token, membered_user, nollning_event, mentor_group):
    """
    Regression: patching some other field of a signup on a nollning event used to be
    rejected with 403, because an omitted group_name was checked as if it were a group
    the user isn't in.
    """
    signup = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mentor_group.name},
        headers=auth_headers(member_token),
    )
    assert signup.status_code in (200, 201), signup.text

    response = client.patch(
        f"/event-signup/{nollning_event['id']}", json={"priority": "Nolla"}, headers=auth_headers(member_token)
    )

    assert response.status_code == 200, response.text
    assert response.json()["priority"] == "Nolla"


def test_update_signup_to_disallowed_group(
    client, member_token, membered_user, nollning_event, mentor_group, mission_group
):
    """Switching to a group of a disallowed type is rejected, and nothing else is changed."""
    signup = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mentor_group.name},
        headers=auth_headers(member_token),
    )
    assert signup.status_code in (200, 201), signup.text

    response = client.patch(
        f"/event-signup/{nollning_event['id']}",
        json={"group_name": mission_group.name, "priority": "Nolla"},
        headers=auth_headers(member_token),
    )

    assert response.status_code == 403
    signup_after = client.get(
        f"/event-signup/me-signup/{nollning_event['id']}", headers=auth_headers(member_token)
    ).json()
    assert signup_after["group_name"] == mentor_group.name
    assert signup_after["priority"] != "Nolla"
