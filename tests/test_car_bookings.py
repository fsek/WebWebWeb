# type: ignore
import pytest
from main import app
from datetime import datetime, timedelta, timezone
from .basic_factories import auth_headers

# Helper to get Stockholm local time (UTC+1 or UTC+2 DST, but for simplicity, use UTC+1)
STOCKHOLM_TZ = timezone(timedelta(hours=1))


def stockholm_dt(year, month, day, hour, minute=0):
    # Create Stockholm time, then convert to UTC
    local = datetime(year, month, day, hour, minute, tzinfo=STOCKHOLM_TZ)
    return local.astimezone(timezone.utc)


def create_booking(client, token, start, end, description="desc", council_id=0, personal=False):
    body = {
        "description": description,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "personal": personal,
        "council_id": council_id,
    }
    return client.post("/car/", json=body, headers=auth_headers(token))


def patch_booking(client, token, booking_id, **kwargs):
    return client.patch(f"/car/{booking_id}", json=kwargs, headers=auth_headers(token))


def test_admin_autoconfirm(client, admin_token, admin_council_id):
    start = stockholm_dt(2030, 1, 8, 10)  # Tuesday
    end = stockholm_dt(2030, 1, 8, 12)
    resp = create_booking(client, admin_token, start, end, "admin booking", council_id=admin_council_id, personal=True)
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert "confirmed" in data
    assert "booking_id" in data
    assert data["confirmed"] is True

    start = stockholm_dt(2030, 1, 8, 6)  # Before office hours
    end = stockholm_dt(2030, 1, 8, 7)
    resp2 = create_booking(client, admin_token, start, end, "early booking", council_id=admin_council_id)
    assert resp2.status_code in (200, 201)
    assert resp2.json()["confirmed"] is True

    start = stockholm_dt(2030, 1, 8, 18)  # After office hours
    end = stockholm_dt(2030, 1, 8, 19)
    resp3 = create_booking(client, admin_token, start, end, "late booking", council_id=admin_council_id)
    assert resp3.status_code in (200, 201)
    assert resp3.json()["confirmed"] is True

    start = stockholm_dt(2030, 1, 12, 10)  # Saturday
    end = stockholm_dt(2030, 1, 12, 12)
    resp4 = create_booking(client, admin_token, start, end, "weekend booking", council_id=admin_council_id)
    assert resp4.status_code in (200, 201)
    assert resp4.json()["confirmed"] is True


def test_user_autoconfirm(client, member_token, member_council_id):
    # Book inside hours
    start = stockholm_dt(2030, 1, 8, 10)
    end = stockholm_dt(2030, 1, 8, 12)
    resp = create_booking(client, member_token, start, end, "user booking", council_id=member_council_id)
    assert resp.status_code in (200, 201)
    assert resp.json()["confirmed"] is True


def test_user_autounconfirm_outside_hours(client, member_token, member_council_id):
    # Before 08:00
    start = stockholm_dt(2030, 1, 8, 7)
    end = stockholm_dt(2030, 1, 8, 9)
    resp = create_booking(client, member_token, start, end, "early booking", council_id=member_council_id)
    assert resp.status_code in (200, 201)
    assert resp.json()["confirmed"] is False

    # After 17:00
    start = stockholm_dt(2030, 1, 8, 18)
    end = stockholm_dt(2030, 1, 8, 19)
    resp = create_booking(client, member_token, start, end, "late booking", council_id=member_council_id)
    assert resp.status_code in (200, 201)
    assert resp.json()["confirmed"] is False


def test_user_autounconfirm_weekend(client, member_token, member_council_id):
    # Saturday
    start = stockholm_dt(2030, 1, 12, 10)
    end = stockholm_dt(2030, 1, 12, 12)
    resp = create_booking(client, member_token, start, end, "weekend booking", council_id=member_council_id)
    assert resp.status_code in (200, 201)
    assert resp.json()["confirmed"] is False


def test_admin_can_confirm_unconfirm(client, admin_token, admin_council_id):
    # Admin creates and then unconfirms
    start = stockholm_dt(2030, 1, 9, 10)
    end = stockholm_dt(2030, 1, 9, 12)
    resp = create_booking(client, admin_token, start, end, "admin confirm", council_id=admin_council_id)
    booking_id = resp.json()["booking_id"]
    assert resp.json()["confirmed"] is True

    # Admin unconfirms
    resp2 = patch_booking(client, admin_token, booking_id, confirmed=False)
    assert resp2.status_code == 200
    assert resp2.json()["confirmed"] is False

    # Admin confirms again
    resp3 = patch_booking(client, admin_token, booking_id, confirmed=True)
    assert resp3.status_code == 200
    assert resp3.json()["confirmed"] is True


def test_user_edit_autounconfirm(client, member_token, member_council_id):
    # User books inside hours
    start = stockholm_dt(2030, 1, 10, 10)
    end = stockholm_dt(2030, 1, 10, 12)
    resp = create_booking(client, member_token, start, end, "user booking", council_id=member_council_id)
    booking_id = resp.json()["booking_id"]
    # Try to edit to outside hours
    new_end = stockholm_dt(2030, 1, 10, 18)
    resp2 = patch_booking(client, member_token, booking_id, end_time=new_end.isoformat())
    assert resp2.status_code == 200
    assert resp2.json()["confirmed"] is False


def test_unconfirmed_overlap_allowed(client, member_token, member_council_id):
    # Book unconfirmed slot
    start = stockholm_dt(2030, 1, 12, 7)
    end = stockholm_dt(2030, 1, 12, 9)
    resp1 = create_booking(client, member_token, start, end, "unconfirmed1", council_id=member_council_id)
    assert resp1.json()["confirmed"] is False
    # Overlapping unconfirmed booking
    resp2 = create_booking(client, member_token, start, end, "unconfirmed2", council_id=member_council_id)
    assert resp2.status_code in (200, 201)
    assert resp2.json()["confirmed"] is False


def test_confirmed_overlap_not_allowed(client, admin_token, admin_council_id):
    # Book confirmed slot
    start = stockholm_dt(2030, 1, 13, 10)
    end = stockholm_dt(2030, 1, 13, 12)
    resp1 = create_booking(client, admin_token, start, end, "confirmed1", council_id=admin_council_id)
    assert resp1.json()["confirmed"] is True
    # Overlapping booking via POST should be auto-unconfirmed
    resp2 = create_booking(client, admin_token, start, end, "confirmed2", council_id=admin_council_id)
    assert resp2.status_code in (200, 201)
    assert resp2.json()["confirmed"] is False


def test_confirmed_overlap_patch_not_allowed(client, admin_token, admin_council_id):
    # Book two non-overlapping confirmed slots
    start1 = stockholm_dt(2030, 1, 15, 8)
    end1 = stockholm_dt(2030, 1, 15, 10)
    start2 = stockholm_dt(2030, 1, 15, 12)
    end2 = stockholm_dt(2030, 1, 15, 14)
    resp1 = create_booking(client, admin_token, start1, end1, "confirmed1", council_id=admin_council_id)
    resp2 = create_booking(client, admin_token, start2, end2, "confirmed2", council_id=admin_council_id)
    id1 = resp1.json()["booking_id"]
    id2 = resp2.json()["booking_id"]
    # Try to patch booking 2 to overlap with booking 1
    patch_resp = patch_booking(client, admin_token, id2, start_time=start1.isoformat(), end_time=end1.isoformat())
    assert patch_resp.status_code >= 400 and patch_resp.status_code < 500


def test_unconfirmed_overlap_patch_allowed(client, member_token, member_council_id):
    # Book two non-overlapping unconfirmed slots
    start1 = stockholm_dt(2030, 1, 18, 7)
    end1 = stockholm_dt(2030, 1, 18, 9)
    start2 = stockholm_dt(2030, 1, 18, 19)
    end2 = stockholm_dt(2030, 1, 18, 21)
    resp1 = create_booking(client, member_token, start1, end1, "unconfirmed1", council_id=member_council_id)
    resp2 = create_booking(client, member_token, start2, end2, "unconfirmed2", council_id=member_council_id)
    assert resp1.json()["confirmed"] is False
    assert resp2.json()["confirmed"] is False

    # Patch booking 2 to overlap with booking 1
    id2 = resp2.json()["booking_id"]
    patch_resp = patch_booking(client, member_token, id2, start_time=start1.isoformat(), end_time=end1.isoformat())
    assert patch_resp.status_code == 200
    assert patch_resp.json()["confirmed"] is False


def test_confirmed_and_unconfirmed_patch_overlap_allowed(
    client, admin_token, member_token, admin_council_id, member_council_id
):
    # Confirmed booking by admin
    start1 = stockholm_dt(2030, 1, 19, 10)
    end1 = stockholm_dt(2030, 1, 19, 12)
    resp1 = create_booking(client, admin_token, start1, end1, "confirmed", council_id=admin_council_id)
    assert resp1.json()["confirmed"] is True

    # Unconfirmed booking by user (not overlapping initially)
    start2 = stockholm_dt(2030, 1, 19, 7)
    end2 = stockholm_dt(2030, 1, 19, 8)
    resp2 = create_booking(client, member_token, start2, end2, "unconfirmed", council_id=member_council_id)
    assert resp2.json()["confirmed"] is False

    # Patch unconfirmed booking to overlap with confirmed
    booking_id = resp2.json()["booking_id"]
    new_end = stockholm_dt(2030, 1, 19, 11)  # Creates overlap
    patch_resp = patch_booking(client, member_token, booking_id, end_time=new_end.isoformat())
    assert patch_resp.status_code == 200
    assert patch_resp.json()["confirmed"] is False


def test_zero_length_booking_not_allowed(client, admin_token, admin_council_id):
    # Try to create a zero-length booking
    start = stockholm_dt(2030, 1, 16, 10)
    end = stockholm_dt(2030, 1, 16, 10)
    resp = create_booking(client, admin_token, start, end, "zero length", council_id=admin_council_id)
    assert resp.status_code >= 400 and resp.status_code < 500
    # Create a valid booking, then try to patch to zero-length
    valid_end = stockholm_dt(2030, 1, 16, 12)
    resp2 = create_booking(client, admin_token, start, valid_end, "valid", council_id=admin_council_id)
    booking_id = resp2.json()["booking_id"]
    patch_resp = patch_booking(
        client, admin_token, booking_id, start_time=start.isoformat(), end_time=start.isoformat()
    )
    assert patch_resp.status_code >= 400 and patch_resp.status_code < 500


def test_confirmed_and_unconfirmed_overlap_allowed(
    client, admin_token, member_token, admin_council_id, member_council_id
):
    # Confirmed booking by admin
    start = stockholm_dt(2030, 1, 14, 10)
    end = stockholm_dt(2030, 1, 14, 12)
    resp1 = create_booking(client, admin_token, start, end, "confirmed", council_id=admin_council_id)
    assert resp1.json()["confirmed"] is True
    # Overlapping unconfirmed booking by user
    start2 = stockholm_dt(2030, 1, 14, 7)
    end2 = stockholm_dt(2030, 1, 14, 14)
    resp2 = create_booking(client, member_token, start2, end2, "unconfirmed overlap", council_id=member_council_id)
    assert resp2.status_code in (200, 201)
    assert resp2.json()["confirmed"] is False


def test_end_before_start_not_allowed(client, admin_token, admin_council_id):
    # Try to create a booking with end before start
    start = stockholm_dt(2030, 1, 17, 12)
    end = stockholm_dt(2030, 1, 17, 10)
    resp = create_booking(client, admin_token, start, end, "end before start", council_id=admin_council_id)
    assert resp.status_code >= 400 and resp.status_code < 500
    # Create a valid booking, then try to patch to end before start
    valid_end = stockholm_dt(2030, 1, 17, 14)
    resp2 = create_booking(client, admin_token, start, valid_end, "valid", council_id=admin_council_id)
    booking_id = resp2.json()["booking_id"]
    patch_resp = patch_booking(client, admin_token, booking_id, start_time=start.isoformat(), end_time=end.isoformat())
    assert patch_resp.status_code >= 400 and patch_resp.status_code < 500


def test_admin_can_select_any_council(client, admin_token, admin_council_id, member_council_id):
    start = stockholm_dt(2030, 3, 1, 10)
    end = stockholm_dt(2030, 3, 1, 12)

    # Admin should be able to book with any council
    resp = create_booking(client, admin_token, start, end, "admin council booking", council_id=admin_council_id)
    assert resp.status_code in (200, 201)
    assert resp.json()["council_id"] == admin_council_id

    resp2 = create_booking(client, admin_token, start, end, "admin other council booking", council_id=member_council_id)
    assert resp2.status_code in (200, 201)
    assert resp2.json()["council_id"] == member_council_id


def test_user_can_select_own_council(client, member_token, member_council_id):
    start = stockholm_dt(2030, 3, 2, 10)
    end = stockholm_dt(2030, 3, 2, 12)

    # User should be able to book with their own council
    resp = create_booking(client, member_token, start, end, "user council booking", council_id=member_council_id)
    assert resp.status_code in (200, 201)
    assert resp.json()["council_id"] == member_council_id


def test_user_cannot_select_other_council(client, member_token, admin_council_id):
    start = stockholm_dt(2030, 3, 3, 10)
    end = stockholm_dt(2030, 3, 3, 12)

    # User should not be able to book with a council they're not part of
    resp = create_booking(client, member_token, start, end, "unauthorized council booking", council_id=admin_council_id)
    assert resp.status_code >= 400 and resp.status_code < 500


def test_admin_edit_council(client, admin_token, admin_council_id, member_council_id):
    start = stockholm_dt(2030, 3, 4, 10)
    end = stockholm_dt(2030, 3, 4, 12)

    # Create booking with one council
    resp = create_booking(client, admin_token, start, end, "admin edit council", council_id=member_council_id)
    booking_id = resp.json()["booking_id"]

    # Admin should be able to change the council
    resp2 = patch_booking(client, admin_token, booking_id, council_id=admin_council_id)
    assert resp2.status_code == 200
    assert resp2.json()["council_id"] == admin_council_id


def test_user_cannot_edit_to_unauthorized_council(client, member_token, member_council_id, admin_council_id):
    start = stockholm_dt(2030, 3, 5, 10)
    end = stockholm_dt(2030, 3, 5, 12)

    # Create booking with authorized council
    resp = create_booking(client, member_token, start, end, "user edit council", council_id=member_council_id)
    booking_id = resp.json()["booking_id"]

    # User should not be able to change to unauthorized council
    resp2 = patch_booking(client, member_token, booking_id, council_id=admin_council_id)
    assert resp2.status_code >= 400 and resp2.status_code < 500


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


def test_edit_personal_flag(client, admin_token, admin_council_id):
    start = stockholm_dt(2030, 3, 8, 10)
    end = stockholm_dt(2030, 3, 8, 12)

    # Create non-personal booking
    resp = create_booking(
        client, admin_token, start, end, "edit personal flag", personal=False, council_id=admin_council_id
    )
    booking_id = resp.json()["booking_id"]

    # Edit to make it personal
    resp2 = patch_booking(client, admin_token, booking_id, personal=True)
    assert resp2.status_code == 200
    assert resp2.json()["personal"] is True

    # Edit back to non-personal without providing council
    resp3 = patch_booking(client, admin_token, booking_id, personal=False)
    assert resp3.status_code >= 400 and resp3.status_code < 500  # Should be blocked

    # Edit back to non-personal with providing council
    resp4 = patch_booking(client, admin_token, booking_id, personal=False, council_id=admin_council_id)
    assert resp4.status_code == 200
    assert resp4.json()["personal"] is False
