# type: ignore
from main import app
from datetime import datetime, timedelta, timezone
from .basic_factories import auth_headers

# Most of this file was copied from the car booking tests, with modifications for room bookings.

# Helper to get Stockholm local time (UTC+1 or UTC+2 DST, but for simplicity, use UTC+1)
STOCKHOLM_TZ = timezone(timedelta(hours=1))


def stockholm_dt(year, month, day, hour, minute=0):
    # Create Stockholm time, then convert to UTC
    local = datetime(year, month, day, hour, minute, tzinfo=STOCKHOLM_TZ)
    return local.astimezone(timezone.utc)


def create_booking(client, token, start, end, description, council_id=None, personal=False, room="LC"):
    body = {
        "room": room,
        "description": description if description else "example description",
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "personal": personal,
    }
    if council_id is not None:
        body["council_id"] = council_id
    return client.post("/rooms/", json=body, headers=auth_headers(token))


def patch_booking(client, token, booking_id, **kwargs):
    return client.patch(f"/rooms/{booking_id}", json=kwargs, headers=auth_headers(token))


def test_room_booking_creation(client, admin_token, admin_council_id):
    start = stockholm_dt(2030, 1, 8, 10)  # Tuesday
    end = stockholm_dt(2030, 1, 8, 12)
    resp = create_booking(client, admin_token, start, end, "admin booking", council_id=admin_council_id, personal=True)
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert "id" in data


def test_overlapping_bookings_not_allowed(client, member_token, member_council_id):
    # Book first slot
    start = stockholm_dt(2030, 1, 11, 10)
    end = stockholm_dt(2030, 1, 11, 12)
    resp1 = create_booking(client, member_token, start, end, "first booking", council_id=member_council_id)
    assert resp1.status_code in (200, 201)

    # Try to book overlapping slot
    start2 = stockholm_dt(2030, 1, 11, 11)
    end2 = stockholm_dt(2030, 1, 11, 13)
    resp2 = create_booking(client, member_token, start2, end2, "overlapping booking", council_id=member_council_id)
    assert resp2.status_code >= 400 and resp2.status_code < 500


def test_admin_overlapping_bookings_not_allowed(client, admin_token, admin_council_id):
    # Book first slot
    start = stockholm_dt(2030, 1, 11, 10)
    end = stockholm_dt(2030, 1, 11, 12)
    resp1 = create_booking(client, admin_token, start, end, "admin first booking", council_id=admin_council_id)
    assert resp1.status_code in (200, 201)

    # Try to book overlapping slot
    start2 = stockholm_dt(2030, 1, 11, 11)
    end2 = stockholm_dt(2030, 1, 11, 13)
    resp2 = create_booking(client, admin_token, start2, end2, "admin overlapping booking", council_id=admin_council_id)
    assert resp2.status_code >= 400 and resp2.status_code < 500


def test_overlap_patch_not_allowed(client, member_token, member_council_id):
    # Book first slot
    start = stockholm_dt(2030, 1, 10, 10)
    end = stockholm_dt(2030, 1, 10, 12)
    resp1 = create_booking(client, member_token, start, end, "first booking", council_id=member_council_id)
    assert resp1.status_code in (200, 201)

    # Book second slot
    start2 = stockholm_dt(2030, 1, 10, 13)
    end2 = stockholm_dt(2030, 1, 10, 15)
    resp2 = create_booking(client, member_token, start2, end2, "second booking", council_id=member_council_id)
    assert resp2.status_code in (200, 201)

    # Try to patch second booking to overlap with first
    id2 = resp2.json()["id"]
    patch_resp = patch_booking(client, member_token, id2, start_time=start.isoformat(), end_time=end.isoformat())
    assert patch_resp.status_code >= 400 and patch_resp.status_code < 500


def test_zero_length_booking_not_allowed(client, admin_token, admin_council_id):
    # Try to create a zero-length booking
    start = stockholm_dt(2030, 1, 16, 10)
    end = stockholm_dt(2030, 1, 16, 10)
    resp = create_booking(client, admin_token, start, end, "zero length", council_id=admin_council_id)
    assert resp.status_code >= 400 and resp.status_code < 500
    # Create a valid booking, then try to patch to zero-length
    valid_end = stockholm_dt(2030, 1, 16, 12)
    resp2 = create_booking(client, admin_token, start, valid_end, "valid", council_id=admin_council_id)
    booking_id = resp2.json()["id"]
    patch_resp = patch_booking(
        client, admin_token, booking_id, start_time=start.isoformat(), end_time=start.isoformat()
    )
    assert patch_resp.status_code >= 400 and patch_resp.status_code < 500


def test_end_before_start_not_allowed(client, admin_token, admin_council_id):
    # Try to create a booking with end before start
    start = stockholm_dt(2030, 1, 17, 12)
    end = stockholm_dt(2030, 1, 17, 10)
    resp = create_booking(client, admin_token, start, end, "end before start", council_id=admin_council_id)
    assert resp.status_code >= 400 and resp.status_code < 500
    # Create a valid booking, then try to patch to end before start
    valid_end = stockholm_dt(2030, 1, 17, 14)
    resp2 = create_booking(client, admin_token, start, valid_end, "valid", council_id=admin_council_id)
    booking_id = resp2.json()["id"]
    patch_resp = patch_booking(client, admin_token, booking_id, start_time=start.isoformat(), end_time=end.isoformat())
    assert patch_resp.status_code >= 400 and patch_resp.status_code < 500


def test_admin_can_select_any_council(client, admin_token, admin_council_id, member_council_id):
    start = stockholm_dt(2030, 3, 1, 10)
    end = stockholm_dt(2030, 3, 1, 12)
    start2 = stockholm_dt(2030, 3, 1, 13)
    end2 = stockholm_dt(2030, 3, 1, 15)

    # Admin should be able to book with any council
    resp = create_booking(client, admin_token, start, end, "admin council booking", council_id=admin_council_id)
    assert resp.status_code in (200, 201)
    assert resp.json()["council"]["id"] == admin_council_id

    resp2 = create_booking(
        client, admin_token, start2, end2, "admin other council booking", council_id=member_council_id
    )
    assert resp2.status_code in (200, 201)
    assert resp2.json()["council"]["id"] == member_council_id


def test_user_can_select_own_council(client, member_token, member_council_id):
    start = stockholm_dt(2030, 3, 2, 10)
    end = stockholm_dt(2030, 3, 2, 12)

    # User should be able to book with their own council
    resp = create_booking(client, member_token, start, end, "user council booking", council_id=member_council_id)
    assert resp.status_code in (200, 201)
    assert resp.json()["council"]["id"] == member_council_id


def test_user_cannot_select_other_council(client, member_token, admin_council_id):
    start = stockholm_dt(2030, 3, 3, 10)
    end = stockholm_dt(2030, 3, 3, 12)

    # User should not be able to book with a council they're not part of
    resp = create_booking(client, member_token, start, end, "unauthorized council booking", council_id=admin_council_id)
    assert resp.status_code >= 400 and resp.status_code < 500


def test_personal_booking_creation_admin(client, admin_token, admin_council_id):
    start = stockholm_dt(2030, 3, 6, 10)
    end = stockholm_dt(2030, 3, 6, 12)

    # Admin creates personal booking
    resp = create_booking(
        client, admin_token, start, end, "admin personal booking", personal=True, council_id=admin_council_id
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["personal"] is True


def test_personal_booking_creation_user(client, member_token, member_council_id):
    start = stockholm_dt(2030, 3, 7, 10)
    end = stockholm_dt(2030, 3, 7, 12)

    # User creates personal booking
    resp = create_booking(
        client, member_token, start, end, "user personal booking", personal=True, council_id=member_council_id
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["personal"] is True


def test_personal_booking_no_council(client, member_token, member_council_id):
    start = stockholm_dt(2030, 3, 14, 10)
    end = stockholm_dt(2030, 3, 14, 12)

    # User creates a personal booking without council_id
    resp = create_booking(client, member_token, start, end, "personal no council", personal=True)
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["personal"] is True
    assert data["council"] is None


def test_patch_allowed_fields(client, admin_token, admin_council_id):
    start = stockholm_dt(2030, 3, 15, 10)
    end = stockholm_dt(2030, 3, 15, 12)

    # Create booking
    resp = create_booking(client, admin_token, start, end, "original description", council_id=admin_council_id)
    booking_id = resp.json()["id"]

    # Test patching allowed fields
    new_end = stockholm_dt(2030, 3, 15, 14)
    resp2 = patch_booking(
        client, admin_token, booking_id, end_time=new_end.isoformat(), description="updated description"
    )
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["description"] == "updated description"


def test_non_member_booking_access(client, non_member_token, member_token):
    start = stockholm_dt(2030, 3, 9, 10)
    end = stockholm_dt(2030, 3, 9, 12)

    # Non-member should not be able to create a booking
    resp = create_booking(client, non_member_token, start, end, "non-member booking", personal=True)
    assert resp.status_code >= 400 and resp.status_code < 500

    # Non-member should not be able to read bookings
    resp2 = client.get("/rooms/get_all", headers=auth_headers(non_member_token))
    assert resp2.status_code >= 400 and resp2.status_code < 500

    # Non-member should not be able to edit bookings
    resp3 = create_booking(client, member_token, start, end, "member booking", personal=True)
    assert resp3.status_code in (200, 201)
    booking_id = resp3.json()["id"]
    resp4 = patch_booking(client, non_member_token, booking_id, description="non-member edit")
    assert resp4.status_code >= 400 and resp4.status_code < 500

    # Non-member should not be able to delete bookings
    resp5 = client.delete(f"/rooms/{booking_id}", headers=auth_headers(non_member_token))
    assert resp5.status_code >= 400 and resp5.status_code < 500


def test_member_delete_own_booking(client, member_token, member_council_id):
    start = stockholm_dt(2030, 3, 10, 10)
    end = stockholm_dt(2030, 3, 10, 12)

    # Member creates a booking
    resp = create_booking(client, member_token, start, end, "member booking", council_id=member_council_id)
    assert resp.status_code in (200, 201)
    booking_id = resp.json()["id"]

    # Member should be able to delete their own booking
    resp2 = client.delete(f"/rooms/{booking_id}", headers=auth_headers(member_token))
    assert resp2.status_code in (200, 204)


def test_member_delete_other_booking(client, member_token, admin_token, admin_council_id):
    start = stockholm_dt(2030, 3, 11, 10)
    end = stockholm_dt(2030, 3, 11, 12)

    # Admin creates a booking
    resp = create_booking(client, admin_token, start, end, "admin booking", council_id=admin_council_id)
    assert resp.status_code in (200, 201)
    booking_id = resp.json()["id"]

    # Member should not be able to delete admin's booking
    resp2 = client.delete(f"/rooms/{booking_id}", headers=auth_headers(member_token))
    assert resp2.status_code >= 400 and resp2.status_code < 500


def test_admin_delete_any_booking(client, admin_token, member_token, member_council_id):
    start = stockholm_dt(2030, 3, 12, 10)
    end = stockholm_dt(2030, 3, 12, 12)

    # Member creates a booking
    resp = create_booking(client, member_token, start, end, "member booking", council_id=member_council_id)
    assert resp.status_code in (200, 201)
    booking_id = resp.json()["id"]

    # Admin should be able to delete the member's booking
    resp2 = client.delete(f"/rooms/{booking_id}", headers=auth_headers(admin_token))
    assert resp2.status_code in (200, 204)


def test_overlap_of_different_rooms_allowed(client, member_token, member_council_id):
    # Book first room
    start = stockholm_dt(2030, 1, 20, 10)
    end = stockholm_dt(2030, 1, 20, 12)
    resp1 = create_booking(
        client, member_token, start, end, "first room booking", council_id=member_council_id, room="LC"
    )
    assert resp1.status_code in (200, 201)

    # Book second room overlapping time
    start2 = stockholm_dt(2030, 1, 20, 11)
    end2 = stockholm_dt(2030, 1, 20, 13)
    resp2 = create_booking(
        client, member_token, start2, end2, "second room booking", council_id=member_council_id, room="SK"
    )
    assert resp2.status_code in (200, 201)
