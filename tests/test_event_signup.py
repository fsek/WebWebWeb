# type: ignore
import pytest
from helpers.constants import DEFAULT_USER_PRIORITY
from .basic_factories import add_user_to_group, add_group_to_current_nollning, auth_headers, event_data_factory


def test_signup_with_allowed_group_type(client, member_token, membered_user, nollning_event, mentor_group):
    """A group whose type is in mentor_group_types is accepted."""
    response = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mentor_group.name, "priority": "Nolla"},
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


def test_signup_with_group_type_from_wrong_year(
    client, member_token, membered_user, nollning_event, last_years_mentor_group
):
    """Signup with a group with the correct type but the wrong year is rejected."""
    response = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": last_years_mentor_group.name},
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


def test_nollning_event_signup_without_group(client, member_token, membered_user, nollning_event, mission_group):
    """Signing up to nollning event without picking a group is not allowed."""
    response = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id},
        headers=auth_headers(member_token),
    )

    assert response.status_code == 403, response.text


def test_nollning_event_signup_without_group_with_post_priority(
    client, admin_token, admin_council_id, member_token, membered_user, member_post
):
    """A user whose post matches one of the event's priorities may sign up without a group."""
    data = event_data_factory(
        council_id=admin_council_id,
        is_nollning_event=True,
        mentor_group_types=["Mentor"],
        priorities=[member_post.name_sv, "Nolla"],
    )
    event = client.post("/events/", json=data, headers=auth_headers(admin_token)).json()

    response = client.post(
        f"/event-signup/{event['id']}",
        json={"user_id": membered_user.id, "priority": member_post.name_sv},
        headers=auth_headers(member_token),
    )

    assert response.status_code in (200, 201), response.text
    assert response.json()["group_name"] is None


def test_non_nollning_event_signup_without_group(client, member_token, membered_user, event, mission_group):
    """Signing up to non-nollning event without picking a group is not restricted by the group types."""
    response = client.post(
        f"/event-signup/{event['id']}",
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
    add_group_to_current_nollning(db_session, group)

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


def test_update_signup_without_changing_group_name_is_allowed(
    client, member_token, membered_user, nollning_event, mentor_group
):
    """Not sending a group name with the update body should make it stay as-is"""
    signup = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mentor_group.name, "priority": "Nolla"},
        headers=auth_headers(member_token),
    )
    assert signup.status_code in (200, 201), signup.text
    assert signup.json()["group_name"] == mentor_group.name

    response = client.patch(
        f"/event-signup/{nollning_event['id']}",
        json={"priority": "Nolla"},
        headers=auth_headers(member_token),
    )

    assert response.status_code == 200, response.text
    assert response.json()["priority"] == "Nolla"
    assert response.json()["group_name"] == mentor_group.name


@pytest.mark.parametrize("sent_group_name", [None, ""])
def test_nollning_event_update_signup_remove_group_name_is_disallowed(
    client, member_token, membered_user, nollning_event, mentor_group, sent_group_name
):
    """Sending a null (or empty) group name to remove the group is disallowed for nollning events"""
    signup = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mentor_group.name, "priority": "Nolla"},
        headers=auth_headers(member_token),
    )
    assert signup.status_code in (200, 201), signup.text
    assert signup.json()["group_name"] == mentor_group.name

    response = client.patch(
        f"/event-signup/{nollning_event['id']}",
        json={"group_name": sent_group_name},
        headers=auth_headers(member_token),
    )

    assert response.status_code == 403, response.text


@pytest.mark.parametrize("sent_group_name", [None, ""])
def test_non_nollning_event_update_signup_remove_group_name_is_allowed(
    client, member_token, membered_user, event, mentor_group, sent_group_name
):
    """Sending a null (or empty) group name to remove the group is allowed for non-nollning events"""
    signup = client.post(
        f"/event-signup/{event['id']}",
        json={"user_id": membered_user.id, "group_name": mentor_group.name},
        headers=auth_headers(member_token),
    )
    assert signup.status_code in (200, 201), signup.text
    assert signup.json()["group_name"] == mentor_group.name

    response = client.patch(
        f"/event-signup/{event['id']}",
        json={"group_name": sent_group_name},
        headers=auth_headers(member_token),
    )

    assert response.status_code == 200, response.text
    assert response.json()["group_name"] is None


def test_update_signup_without_priority_keeps_priority(
    client, member_token, membered_user, nollning_event, mentor_group
):
    """Leaving priority out of the update body should make it stay as-is"""
    signup = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mentor_group.name, "priority": "Nolla"},
        headers=auth_headers(member_token),
    )
    assert signup.status_code in (200, 201), signup.text
    assert signup.json()["priority"] == "Nolla"

    response = client.patch(
        f"/event-signup/{nollning_event['id']}",
        json={"drinkPackage": "Alcohol"},
        headers=auth_headers(member_token),
    )

    assert response.status_code == 200, response.text
    assert response.json()["priority"] == "Nolla"
    assert response.json()["group_name"] == mentor_group.name


def test_update_signup_with_null_priority_resets_to_default(
    client, admin_token, member_token, membered_user, nollning_event
):
    """Sending a null priority should reset it to the default one, for a user who does not match
    any of the event's priorities and may therefore hold the default one.
    This should only happen if a user loses their role, or is added to the
    event by an admin (as done here)."""
    signup = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "priority": "Nolla"},
        headers=auth_headers(admin_token),
    )
    assert signup.status_code in (200, 201), signup.text
    assert signup.json()["priority"] == "Nolla"

    response = client.patch(
        f"/event-signup/{nollning_event['id']}",
        json={"priority": None},
        headers=auth_headers(member_token),
    )

    assert response.status_code == 200, response.text
    assert response.json()["priority"] == DEFAULT_USER_PRIORITY


def test_signup_with_priority_the_user_does_not_have(client, member_token, membered_user, nollning_event, mentor_group):
    """A mentee is not a gruppfadder, so we reject the signup even if the event allows the priority"""
    response = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mentor_group.name, "priority": "Gruppfadder"},
        headers=auth_headers(member_token),
    )

    assert response.status_code == 403, response.text


def test_signup_with_priority_not_on_the_event(
    client, admin_token, admin_council_id, member_token, membered_user, member_post
):
    """Signups with a post priority the user holds but which the event does not ask for is rejected."""
    data = event_data_factory(council_id=admin_council_id, priorities=["Nolla"])
    event = client.post("/events/", json=data, headers=auth_headers(admin_token)).json()

    response = client.post(
        f"/event-signup/{event['id']}",
        json={"user_id": membered_user.id, "priority": member_post.name_sv},
        headers=auth_headers(member_token),
    )

    assert response.status_code == 403, response.text


def test_admin_can_sign_up_user_with_any_priority(client, admin_token, membered_user, nollning_event, mentor_group):
    """Admins make the final call and are not restricted by the priorities."""
    response = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mentor_group.name, "priority": "Gruppfadder"},
        headers=auth_headers(admin_token),
    )

    assert response.status_code in (200, 201), response.text
    assert response.json()["priority"] == "Gruppfadder"


def test_update_signup_to_priority_the_user_does_not_have(
    client, member_token, membered_user, nollning_event, mentor_group
):
    """Switching to a priority the user does not have is rejected, and nothing else is changed."""
    signup = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mentor_group.name, "priority": "Nolla"},
        headers=auth_headers(member_token),
    )
    assert signup.status_code in (200, 201), signup.text

    response = client.patch(
        f"/event-signup/{nollning_event['id']}",
        json={"priority": "Uppdragsfadder", "drinkPackage": "Alcohol"},
        headers=auth_headers(member_token),
    )

    assert response.status_code == 403, response.text
    signup_after = client.get(
        f"/event-signup/me-signup/{nollning_event['id']}", headers=auth_headers(member_token)
    ).json()
    assert signup_after["priority"] == "Nolla"
    assert signup_after["drinkPackage"] == "None"


def test_update_signup_to_disallowed_group(
    client, member_token, membered_user, nollning_event, mentor_group, mission_group
):
    """Switching to a group of a disallowed type is rejected, and nothing else is changed."""
    signup = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mentor_group.name, "priority": "Nolla"},
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


def test_signup_with_default_priority_when_matching_a_priority_is_blocked(
    client, member_token, membered_user, nollning_event, mentor_group
):
    """A nolla who signs up as "Övrigt" is confusing, so we reject it."""
    response = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mentor_group.name, "priority": DEFAULT_USER_PRIORITY},
        headers=auth_headers(member_token),
    )

    assert response.status_code == 403, response.text


@pytest.mark.parametrize("sent_priority", [None, ""])
def test_signup_without_priority_when_matching_a_priority_is_blocked(
    client, member_token, membered_user, nollning_event, mentor_group, sent_priority
):
    """Leaving the priority out is the same as sending "Övrigt", and is rejected the same way."""
    body = {"user_id": membered_user.id, "group_name": mentor_group.name}
    if sent_priority is not None:
        body["priority"] = sent_priority

    response = client.post(
        f"/event-signup/{nollning_event['id']}",
        json=body,
        headers=auth_headers(member_token),
    )

    assert response.status_code == 403, response.text


def test_signup_with_matching_priority_is_still_allowed(
    client, member_token, membered_user, nollning_event, mentor_group
):
    """The priority the user actually holds is of course still accepted."""
    response = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mentor_group.name, "priority": "Nolla"},
        headers=auth_headers(member_token),
    )

    assert response.status_code in (200, 201), response.text
    assert response.json()["priority"] == "Nolla"


def test_signup_with_default_priority_without_matching_a_priority_is_allowed(
    client, member_token, membered_user, admin_token, admin_council_id
):
    """Someone who matches none of the event's priorities keeps the default one."""
    data = event_data_factory(council_id=admin_council_id, priorities=["Nolla"])
    event = client.post("/events/", json=data, headers=auth_headers(admin_token)).json()

    response = client.post(
        f"/event-signup/{event['id']}",
        json={"user_id": membered_user.id, "priority": DEFAULT_USER_PRIORITY},
        headers=auth_headers(member_token),
    )

    assert response.status_code in (200, 201), response.text
    assert response.json()["priority"] == DEFAULT_USER_PRIORITY


def test_signup_with_default_priority_on_event_without_priorities_is_allowed(
    client,
    member_token,
    membered_user,
    event,
    mentor_group,  # Member has a nolla priority, but that doesn't matter since the event has no priorities
):
    """An event which asks for no priorities cannot be matched, so the default one is fine."""
    response = client.post(
        f"/event-signup/{event['id']}",
        json={"user_id": membered_user.id, "priority": DEFAULT_USER_PRIORITY},
        headers=auth_headers(member_token),
    )

    assert response.status_code in (200, 201), response.text
    assert response.json()["priority"] == DEFAULT_USER_PRIORITY


def test_signup_with_default_priority_when_matching_a_post_priority_is_blocked(
    client, member_token, membered_user, member_post, admin_token, admin_council_id
):
    """Post priorities count as a match just like the nollning ones do.
    We reject a signup with the default priority if the user has a post which
    matches one of the event's priorities."""
    data = event_data_factory(council_id=admin_council_id, priorities=[member_post.name_sv])
    event = client.post("/events/", json=data, headers=auth_headers(admin_token)).json()

    response = client.post(
        f"/event-signup/{event['id']}",
        json={"user_id": membered_user.id, "priority": DEFAULT_USER_PRIORITY},
        headers=auth_headers(member_token),
    )

    assert response.status_code == 403, response.text


def test_admin_can_sign_up_matching_user_with_default_priority(
    client, admin_token, membered_user, nollning_event, mentor_group
):
    """Admins make the final call and are not restricted by the priorities."""
    response = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mentor_group.name, "priority": DEFAULT_USER_PRIORITY},
        headers=auth_headers(admin_token),
    )

    assert response.status_code in (200, 201), response.text
    assert response.json()["priority"] == DEFAULT_USER_PRIORITY


def test_update_signup_to_default_priority_when_matching_a_priority_is_blocked(
    client, member_token, membered_user, nollning_event, mentor_group
):
    """The same rule holds when editing an existing signup."""
    signup = client.post(
        f"/event-signup/{nollning_event['id']}",
        json={"user_id": membered_user.id, "group_name": mentor_group.name, "priority": "Nolla"},
        headers=auth_headers(member_token),
    )
    assert signup.status_code in (200, 201), signup.text

    response = client.patch(
        f"/event-signup/{nollning_event['id']}",
        json={"priority": DEFAULT_USER_PRIORITY},
        headers=auth_headers(member_token),
    )

    assert response.status_code == 403, response.text
    signup_after = client.get(
        f"/event-signup/me-signup/{nollning_event['id']}", headers=auth_headers(member_token)
    ).json()
    assert signup_after["priority"] == "Nolla"
