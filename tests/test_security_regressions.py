# type: ignore
"""
Regression tests for security fixes.
"""

import datetime

import pytest

from db_models.council_model import Council_DB
from db_models.event_model import Event_DB
from db_models.user_door_access_model import UserDoorAccess_DB

from .basic_factories import auth_headers


@pytest.fixture()
def simple_event(db_session):
    """A minimal event with signups unconfirmed."""
    council = Council_DB(
        name_sv="EventUtskott",
        description_sv="beskrivning",
        name_en="EventCouncil",
        description_en="description",
    )
    db_session.add(council)
    db_session.commit()

    now = datetime.datetime.now(datetime.timezone.utc)
    event = Event_DB(
        council_id=council.id,
        starts_at=now + datetime.timedelta(days=2),
        ends_at=now + datetime.timedelta(days=3),
        signup_start=now - datetime.timedelta(days=1),
        signup_end=now + datetime.timedelta(days=1),
        title_sv="Testevent",
        title_en="Test event",
        description_sv="beskrivning",
        description_en="description",
        location="LC",
        dress_code="Cool",
        price=0,
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


####################################################################
# Posts: the member roster of a post was world-readable
####################################################################


def test_post_users_requires_authentication(client, member_post):
    """
    Listing who holds a post discloses guild members' names. The sibling route
    GET /posts/ already requires membership; this one must match.
    """
    res = client.get(f"/posts/users/{member_post.id}")

    assert res.status_code == 401, res.text


def test_post_users_allowed_for_member(client, member_token, member_post, membered_user):
    """Members must still be able to read a post's roster."""
    res = client.get(
        f"/posts/users/{member_post.id}",
        headers=auth_headers(member_token),
    )

    assert res.status_code == 200, res.text
    assert membered_user.id in [user["id"] for user in res.json()]


####################################################################
# Door access serving: malformed stil-ids must never be served
####################################################################


def _make_user_with_door_access(db_session, client, email, stil_id, door="Arkivet"):
    from .basic_factories import create_membered_user

    user = create_membered_user(client, db_session, email=email, first_name="Door", last_name="User")
    user.stil_id = stil_id
    db_session.commit()

    now = datetime.datetime.now(datetime.timezone.utc)
    access = UserDoorAccess_DB(
        user_id=user.id,
        door=door,
        starttime=now - datetime.timedelta(days=1),
        endtime=now + datetime.timedelta(days=1),
    )
    db_session.add(access)
    db_session.commit()
    return user


def test_access_serve_filters_all_malformed_stil_ids(client, db_session):
    """
    The endpoint's output is interpolated into HTML by the frontend (after more html removal there),
    so the non-alphanumeric failsafe is a security control. It previously mutated the
    list while iterating over it, which silently skipped entries: with two
    adjacent bad ids, the second one survived and was served.
    """
    # Chosen so that, sorted, the two malformed ids land next to each other.
    _make_user_with_door_access(db_session, client, "door_a@example.com", "aaa<script>")
    _make_user_with_door_access(db_session, client, "door_b@example.com", "aab<img/onerror=x>")
    _make_user_with_door_access(db_session, client, "door_c@example.com", "abc-1234")

    res = client.get("/access-serve/Arkivet")

    assert res.status_code == 200, res.text
    served = res.json()

    assert served == ["abc-1234"], f"malformed stil-ids leaked into output: {served}"
    for stil_id in served:
        assert stil_id.replace("-", "").isalnum()


####################################################################
# CSV exports: member-controlled text must not become a formula
####################################################################


@pytest.mark.parametrize(
    "payload",
    [
        "=cmd|'/c calc'!A1",
        "+1+1",
        "-1+1",
        "@SUM(1+1)",
        "\t=1+1",
        "\r=1+1",
    ],
)
def test_escape_csv_value_neutralizes_formula_triggers(payload):
    from helpers.csv_response_factory import escape_csv_value

    escaped = escape_csv_value(payload)

    assert not escaped.startswith(("=", "+", "-", "@", "\t", "\r"))


def test_escape_csv_value_leaves_ordinary_text_alone():
    from helpers.csv_response_factory import escape_csv_value

    for value in ["Anna", "Vegetarian, Gluten", "", "abc-1234", "1+1"]:
        assert escape_csv_value(value) == value


def test_event_csv_export_escapes_member_supplied_text(client, db_session, admin_token, membered_user, simple_event):
    """
    End to end: a member sets a spreadsheet formula as their free-text food
    preference, an admin exports the signup CSV. The formula must arrive
    quoted, not live, since the admin is the one who opens the file.
    """
    from db_models.event_user_model import EventUser_DB

    membered_user.other_food_preferences = "=cmd|'/c calc'!A1"
    membered_user.first_name = '=HYPERLINK("http://evil.example","click")'
    db_session.commit()

    signup = EventUser_DB(
        user=membered_user,
        user_id=membered_user.id,
        event=simple_event,
        event_id=simple_event.id,
    )
    signup.confirmed_status = True
    db_session.add(signup)
    db_session.commit()

    res = client.get(
        f"/events/event-signups/confirmed/{simple_event.id}/csv",
        headers=auth_headers(admin_token),
    )

    assert res.status_code == 200, res.text
    body = res.text

    assert "=cmd|" in body, "the value should still be present, just neutralized"
    # No cell may begin with a formula trigger.
    import csv as csv_module
    import io

    for row in csv_module.reader(io.StringIO(body)):
        for cell in row:
            assert not cell.startswith(
                ("=", "+", "-", "@", "\t", "\r")
            ), f"cell would be evaluated as a formula: {cell!r}"
