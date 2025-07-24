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


def create_booking(client, token, start, end, description, council_id=None, personal=False):
    body = {
        "description": description if description else "example description",
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "personal": personal,
    }
    if council_id is not None:
        body["council_id"] = council_id
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


def test_overlapping_bookings_not_allowed(client, member_token, member_council_id):
    # Book first slot
    start = stockholm_dt(2030, 1, 11, 10)
    end = stockholm_dt(2030, 1, 11, 12)
    resp1 = create_booking(client, member_token, start, end, "first booking", council_id=member_council_id)
    assert resp1.status_code in (200, 201)
    assert resp1.json()["confirmed"] is True

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
    assert resp1.json()["confirmed"] is True

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
    assert resp1.json()["confirmed"] is True

    # Book second slot
    start2 = stockholm_dt(2030, 1, 10, 13)
    end2 = stockholm_dt(2030, 1, 10, 15)
    resp2 = create_booking(client, member_token, start2, end2, "second booking", council_id=member_council_id)
    assert resp2.status_code in (200, 201)
    assert resp2.json()["confirmed"] is True

    # Try to patch second booking to overlap with first
    id2 = resp2.json()["booking_id"]
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
    booking_id = resp2.json()["booking_id"]
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
    booking_id = resp2.json()["booking_id"]
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
    assert resp.json()["council_id"] == admin_council_id

    resp2 = create_booking(
        client, admin_token, start2, end2, "admin other council booking", council_id=member_council_id
    )
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


# Test council_id not required for personal bookings
def test_personal_booking_no_council(client, member_token, member_council_id):
    start = stockholm_dt(2030, 3, 14, 10)
    end = stockholm_dt(2030, 3, 14, 12)

    # User creates a personal booking without council_id
    resp = create_booking(client, member_token, start, end, "personal no council", personal=True)
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["personal"] is True
    assert data["council_id"] is None


# Test non-members cannot CRUD bookings
def test_non_member_booking_access(client, non_member_token, member_token):
    start = stockholm_dt(2030, 3, 9, 10)
    end = stockholm_dt(2030, 3, 9, 12)

    # Non-member should not be able to create a booking
    resp = create_booking(client, non_member_token, start, end, "non-member booking", personal=True)
    assert resp.status_code >= 400 and resp.status_code < 500

    # Non-member should not be able to read bookings
    resp2 = client.get("/car/", headers=auth_headers(non_member_token))
    assert resp2.status_code >= 400 and resp2.status_code < 500

    # Non-member should not be able to edit bookings
    resp3 = create_booking(client, member_token, start, end, "member booking", personal=True)
    assert resp3.status_code in (200, 201)
    booking_id = resp3.json()["booking_id"]
    resp4 = patch_booking(client, non_member_token, booking_id, description="non-member edit", personal=True)
    assert resp4.status_code >= 400 and resp4.status_code < 500

    # Non-member should not be able to delete bookings
    resp5 = client.delete(f"/car/{booking_id}", headers=auth_headers(non_member_token))
    assert resp5.status_code >= 400 and resp5.status_code < 500


# Test members can delete their own bookings
def test_member_delete_own_booking(client, member_token, member_council_id):
    start = stockholm_dt(2030, 3, 10, 10)
    end = stockholm_dt(2030, 3, 10, 12)

    # Member creates a booking
    resp = create_booking(client, member_token, start, end, "member booking", council_id=member_council_id)
    assert resp.status_code in (200, 201)
    booking_id = resp.json()["booking_id"]

    # Member should be able to delete their own booking
    resp2 = client.delete(f"/car/{booking_id}", headers=auth_headers(member_token))
    assert resp2.status_code in (200, 204)


# Test members cannot delete other members' bookings
def test_member_delete_other_booking(client, member_token, admin_token, admin_council_id):
    start = stockholm_dt(2030, 3, 11, 10)
    end = stockholm_dt(2030, 3, 11, 12)

    # Admin creates a booking
    resp = create_booking(client, admin_token, start, end, "admin booking", council_id=admin_council_id)
    assert resp.status_code in (200, 201)
    booking_id = resp.json()["booking_id"]

    # Member should not be able to delete admin's booking
    resp2 = client.delete(f"/car/{booking_id}", headers=auth_headers(member_token))
    assert resp2.status_code >= 400 and resp2.status_code < 500


# Test admin can delete any booking
def test_admin_delete_any_booking(client, admin_token, member_token, member_council_id):
    start = stockholm_dt(2030, 3, 12, 10)
    end = stockholm_dt(2030, 3, 12, 12)

    # Member creates a booking
    resp = create_booking(client, member_token, start, end, "member booking", council_id=member_council_id)
    assert resp.status_code in (200, 201)
    booking_id = resp.json()["booking_id"]

    # Admin should be able to delete the member's booking
    resp2 = client.delete(f"/car/{booking_id}", headers=auth_headers(admin_token))
    assert resp2.status_code in (200, 204)

