# type: ignore
import pytest
from datetime import datetime, timedelta, timezone
from helpers.constants import DEFAULT_USER_PRIORITY
from .basic_factories import (
    add_user_to_group,
    auth_headers,
    create_membered_user,
    event_data_factory,
)


class TestCreateEvent:
    """Test POST /events/ endpoint"""

    def test_create_event_success(self, client, admin_token, admin_council_id):
        """Admin can create an event and gets the stored values back."""
        data = event_data_factory(council_id=admin_council_id)

        response = client.post("/events/", json=data, headers=auth_headers(admin_token))

        assert response.status_code in (200, 201), response.text
        event = response.json()
        assert event["title_sv"] == data["title_sv"]
        assert event["council_id"] == admin_council_id
        assert event["price"] == data["price"]
        assert event["signup_count"] == 0

    def test_create_nollning_event_with_group_types(self, client, admin_token, admin_council_id):
        """The nollning group settings are persisted as given."""
        data = event_data_factory(
            council_id=admin_council_id,
            is_nollning_event=True,
            mentor_group_types=["Mentor", "Mission"],
            allow_other_mentors=True,
        )

        response = client.post("/events/", json=data, headers=auth_headers(admin_token))

        assert response.status_code in (200, 201), response.text
        event = response.json()
        assert event["is_nollning_event"] is True
        assert event["mentor_group_types"] == ["Mentor", "Mission"]
        assert event["allow_other_mentors"] is True

    def test_create_event_negative_price(self, client, admin_token, admin_council_id):
        """Negative prices are rejected."""
        data = event_data_factory(council_id=admin_council_id, price=-1)

        response = client.post("/events/", json=data, headers=auth_headers(admin_token))

        assert response.status_code == 400

    def test_create_event_ends_before_starts(self, client, admin_token, admin_council_id):
        """An event cannot end before it starts."""
        default_data = event_data_factory()
        data = event_data_factory(
            council_id=admin_council_id, starts_at=default_data["ends_at"], ends_at=default_data["starts_at"]
        )

        response = client.post("/events/", json=data, headers=auth_headers(admin_token))

        assert response.status_code == 400

    @pytest.mark.parametrize("token_fixture", ["member_token", "non_member_token"])
    def test_create_event_forbidden(self, client, request, admin_council_id, token_fixture):
        """Members and non-members cannot create events."""
        token = request.getfixturevalue(token_fixture)
        data = event_data_factory(council_id=admin_council_id)

        response = client.post("/events/", json=data, headers=auth_headers(token))

        assert response.status_code == 403

    def test_create_event_unauthenticated(self, client, admin_council_id):
        """Unauthenticated requests get 401."""
        response = client.post("/events/", json=event_data_factory(council_id=admin_council_id))

        assert response.status_code == 401


class TestGetEvents:
    """Test GET /events/ and GET /events/{eventId} endpoints"""

    def test_get_all_events(self, client, event):
        """Created events are listed."""
        response = client.get("/events/")

        assert response.status_code == 200
        assert event["id"] in [listed["id"] for listed in response.json()]

    def test_get_single_event(self, client, event):
        """A single event can be fetched by id."""
        response = client.get(f"/events/{event['id']}")

        assert response.status_code == 200
        assert response.json()["title_en"] == event["title_en"]


class TestUpdateEvent:
    """Test PATCH /events/{event_id} endpoint"""

    def test_update_event_success(self, client, admin_token, event):
        """Admin can patch a subset of the fields, leaving the rest alone."""
        response = client.patch(
            f"/events/{event['id']}", json={"title_sv": "Nytt namn", "price": 100}, headers=auth_headers(admin_token)
        )

        assert response.status_code == 200
        assert response.json()["title_sv"] == "Nytt namn"
        assert response.json()["price"] == 100
        assert response.json()["title_en"] == event["title_en"]

    def test_update_event_group_settings(self, client, admin_token, nollning_event):
        """The nollning group settings can be changed after creation."""
        response = client.patch(
            f"/events/{nollning_event['id']}",
            json={"mentor_group_types": ["Mission"], "allow_other_mentors": True},  # Mentor before
            headers=auth_headers(admin_token),
        )

        assert response.status_code == 200
        assert response.json()["mentor_group_types"] == ["Mission"]
        assert response.json()["allow_other_mentors"] is True

    def test_update_event_lottery(self, client, admin_token, event):
        """Lottery can be toggled through the update endpoint."""
        assert event["lottery"] is False

        response = client.patch(f"/events/{event['id']}", json={"lottery": True}, headers=auth_headers(admin_token))

        assert response.status_code == 200
        assert response.json()["lottery"] is True

    def test_update_event_negative_price(self, client, admin_token, event):
        """Negative prices are rejected on update too."""
        response = client.patch(f"/events/{event['id']}", json={"price": -5}, headers=auth_headers(admin_token))

        assert response.status_code == 400

    def test_update_event_forbidden(self, client, member_token, event):
        """Members cannot update events."""
        response = client.patch(
            f"/events/{event['id']}", json={"title_sv": "Kapad"}, headers=auth_headers(member_token)
        )

        assert response.status_code == 403


class TestDeleteEvent:
    """Test DELETE /events/{event_id} endpoint"""

    def test_delete_event_success(self, client, admin_token, event):
        """Admin can delete an event, after which it is gone."""
        response = client.delete(f"/events/{event['id']}", headers=auth_headers(admin_token))

        assert response.status_code == 200
        assert client.get(f"/events/{event['id']}").status_code == 404

    def test_delete_event_forbidden(self, client, member_token, event):
        """Members cannot delete events."""
        response = client.delete(f"/events/{event['id']}", headers=auth_headers(member_token))

        assert response.status_code == 403


def _close_signup(db_session, event_id):
    """Move the signup deadline into the past so that spots may be handed out."""
    from db_models.event_model import Event_DB

    event = db_session.query(Event_DB).filter_by(id=event_id).one()
    event.signup_end = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()

    return event


def _signup_users(client, db_session, admin_token, event_id, count, priority, email_prefix):
    """Sign `count` fresh users up to the event as an admin, which bypasses the signup checks."""
    users = []
    for i in range(count):
        user = create_membered_user(client, db_session, email=f"{email_prefix}{i}@example.com")
        response = client.post(
            f"/event-signup/{event_id}",
            json={"user_id": user.id, "priority": priority},
            headers=auth_headers(admin_token),
        )
        assert response.status_code in (200, 201), response.text
        users.append(user)

    return users


def _hand_out_spots(client, admin_token, event_id):
    return client.post(f"/events/event-signups/{event_id}", headers=auth_headers(admin_token))


def _confirmed_signups(client, admin_token, event_id):
    response = client.get(f"/events/event-signups/all/{event_id}", headers=auth_headers(admin_token))
    assert response.status_code == 200, response.text

    return [signup for signup in response.json() if signup["confirmed_status"]]


class TestHandOutSpots:
    """Test POST /events/event-signups/{event_id}, the "dela ut platser" endpoint"""

    def test_prioritized_people_do_not_exceed_max_event_users(self, client, db_session, admin_token, admin_council_id):
        """More prioritized signups than seats must not confirm more people than there are seats."""
        data = event_data_factory(council_id=admin_council_id, max_event_users=2, priorities=["Nolla"])
        event = client.post("/events/", json=data, headers=auth_headers(admin_token)).json()

        _signup_users(client, db_session, admin_token, event["id"], 3, "Nolla", "nolla")
        _close_signup(db_session, event["id"])

        response = _hand_out_spots(client, admin_token, event["id"])

        assert response.status_code in (200, 201), response.text
        assert len(response.json()) == 2
        assert len(_confirmed_signups(client, admin_token, event["id"])) == 2

    def test_oversubscribed_priority_does_not_let_in_non_prioritized_people(
        self, client, db_session, admin_token, admin_council_id
    ):
        """The negative `places_left` must not be used as a slice, which would admit extra people."""
        data = event_data_factory(council_id=admin_council_id, max_event_users=2, priorities=["Nolla"])
        event = client.post("/events/", json=data, headers=auth_headers(admin_token)).json()

        _signup_users(client, db_session, admin_token, event["id"], 3, "Nolla", "nolla")
        _signup_users(client, db_session, admin_token, event["id"], 3, DEFAULT_USER_PRIORITY, "ovrig")
        _close_signup(db_session, event["id"])

        response = _hand_out_spots(client, admin_token, event["id"])

        assert response.status_code in (200, 201), response.text
        confirmed = _confirmed_signups(client, admin_token, event["id"])
        assert len(confirmed) == 2
        assert all(signup["priority"] == "Nolla" for signup in confirmed)

    def test_lottery_event_also_stops_at_max_event_users(self, client, db_session, admin_token, admin_council_id):
        """The lottery branch is capped just like the FIFO one."""
        data = event_data_factory(council_id=admin_council_id, max_event_users=2, priorities=["Nolla"], lottery=True)
        event = client.post("/events/", json=data, headers=auth_headers(admin_token)).json()

        _signup_users(client, db_session, admin_token, event["id"], 4, "Nolla", "nolla")
        _signup_users(client, db_session, admin_token, event["id"], 2, DEFAULT_USER_PRIORITY, "ovrig")
        _close_signup(db_session, event["id"])

        response = _hand_out_spots(client, admin_token, event["id"])

        assert response.status_code in (200, 201), response.text
        confirmed = _confirmed_signups(client, admin_token, event["id"])
        assert len(confirmed) == 2
        assert all(signup["priority"] == "Nolla" for signup in confirmed)

    def test_places_left_are_filled_with_non_prioritized_people(
        self, client, db_session, admin_token, admin_council_id
    ):
        """Seats the prioritized people do not use are still handed out to everyone else."""
        data = event_data_factory(council_id=admin_council_id, max_event_users=3, priorities=["Nolla"])
        event = client.post("/events/", json=data, headers=auth_headers(admin_token)).json()

        prioritized = _signup_users(client, db_session, admin_token, event["id"], 1, "Nolla", "nolla")
        _signup_users(client, db_session, admin_token, event["id"], 4, DEFAULT_USER_PRIORITY, "ovrig")
        _close_signup(db_session, event["id"])

        response = _hand_out_spots(client, admin_token, event["id"])

        assert response.status_code in (200, 201), response.text
        confirmed = _confirmed_signups(client, admin_token, event["id"])
        assert len(confirmed) == 3
        assert prioritized[0].id in {signup["user"]["id"] for signup in confirmed}
