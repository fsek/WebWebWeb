# type: ignore
import pytest
from fastapi.testclient import TestClient
from main import app
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from database import engine

client = TestClient(app)

# Helper to get Stockholm local time (UTC+1 or UTC+2 DST, but for simplicity, use UTC+1)
STOCKHOLM_TZ = timezone(timedelta(hours=1))


def stockholm_dt(year, month, day, hour, minute=0):
    # Create Stockholm time, then convert to UTC
    local = datetime(year, month, day, hour, minute, tzinfo=STOCKHOLM_TZ)
    return local.astimezone(timezone.utc)


# Example users
boss = {
    "email": "boss@fsektionen.se",
    "first_name": "Boss",
    "last_name": "AllaPostersson",
    "password": "dabdab",
    "telephone_number": "+46760187158",
    "program": "F",
}
user = {
    "email": "user2@fsektionen.se",
    "first_name": "User2",
    "last_name": "Userström2",
    "password": "dabdab",
    "telephone_number": "+46706427444",
    "program": "F",
}


@pytest.fixture(autouse=True)
def truncate_car_bookings():
    """Truncate car bookings before each test to avoid overlap issues."""
    with engine.begin() as connection:
        connection.execute(text("DELETE FROM car_booking_table"))
    yield
    # No cleanup after test needed


@pytest.fixture(scope="module")
def boss_token():
    client.post("/auth/register", json=boss)
    resp = client.post("/auth/login", data={"username": boss["email"], "password": boss["password"]})
    return resp.json()["access_token"]


@pytest.fixture(scope="module")
def user_token():
    client.post("/auth/register", json=user)
    resp = client.post("/auth/login", data={"username": user["email"], "password": user["password"]})
    return resp.json()["access_token"]


# New fixtures for councils
@pytest.fixture(scope="module")
def councils():
    # Get councils from the test database
    resp = client.get("/council/")
    assert resp.status_code == 200
    return resp.json()


@pytest.fixture(scope="module")
def user_council_id(councils, user_token):
    # Create a council or get an existing one and assign the user to it
    council_id = councils[0]["id"]
    # Add the user to the council
    resp = client.post(
        f"/council/{council_id}/user", json={"user_id": get_user_id(user_token)}, headers=auth_headers(user_token)
    )
    return council_id


@pytest.fixture(scope="module")
def non_user_council_id(councils):
    # Return a council ID that the regular user is not part of
    # Assuming there are at least 2 councils
    return councils[1]["id"]


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def get_user_id(token):
    resp = client.get("/auth/me", headers=auth_headers(token))
    assert resp.status_code == 200
    return resp.json()["id"]


def create_booking(token, start, end, description="desc", council_id=1, personal=False):
    body = {
        "description": description,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "personal": personal,
        "council_id": council_id,
    }
    print("REQUEST BODY:", body)
    return client.post("/car/", json=body, headers=auth_headers(token))


def patch_booking(token, booking_id, **kwargs):
    return client.patch(f"/car/{booking_id}", json=kwargs, headers=auth_headers(token))


def get_booking(token, booking_id):
    return client.get(f"/car/{booking_id}", headers=auth_headers(token))


def test_admin_autoconfirm(boss_token):
    start = stockholm_dt(2030, 1, 8, 10)
    end = stockholm_dt(2030, 1, 8, 12)
    resp = create_booking(boss_token, start, end, "admin booking", council_id=1, personal=True)
    assert resp.status_code == 200
    data = resp.json()
    assert "confirmed" in data
    assert "booking_id" in data
    assert data["confirmed"] is True


def test_user_autounconfirm_outside_hours(user_token):
    # Before 08:00
    start = stockholm_dt(2030, 1, 8, 7)
    end = stockholm_dt(2030, 1, 8, 9)
    resp = create_booking(user_token, start, end, "early booking")
    assert resp.status_code == 200
    assert resp.json()["confirmed"] is False

    # After 17:00
    start = stockholm_dt(2030, 1, 8, 18)
    end = stockholm_dt(2030, 1, 8, 19)
    resp = create_booking(user_token, start, end, "late booking")
    assert resp.status_code == 200
    assert resp.json()["confirmed"] is False


def test_user_autounconfirm_weekend(user_token):
    # Saturday
    start = stockholm_dt(2030, 1, 12, 10)
    end = stockholm_dt(2030, 1, 12, 12)
    resp = create_booking(user_token, start, end, "weekend booking")
    assert resp.status_code == 200
    assert resp.json()["confirmed"] is False


def test_admin_can_confirm_unconfirm(boss_token):
    # Admin creates and then unconfirms
    start = stockholm_dt(2030, 1, 9, 10)
    end = stockholm_dt(2030, 1, 9, 12)
    resp = create_booking(boss_token, start, end, "admin confirm")
    booking_id = resp.json()["booking_id"]
    assert resp.json()["confirmed"] is True

    # Admin unconfirms
    resp2 = patch_booking(boss_token, booking_id, confirmed=False)
    assert resp2.status_code == 200
    assert resp2.json()["confirmed"] is False

    # Admin confirms again
    resp3 = patch_booking(boss_token, booking_id, confirmed=True)
    assert resp3.status_code == 200
    assert resp3.json()["confirmed"] is True


def test_user_edit_autounconfirm(user_token):
    # User books inside hours
    start = stockholm_dt(2030, 1, 10, 10)
    end = stockholm_dt(2030, 1, 10, 12)
    resp = create_booking(user_token, start, end, "user booking")
    booking_id = resp.json()["booking_id"]
    # Try to edit to outside hours
    new_end = stockholm_dt(2030, 1, 10, 18)
    resp2 = patch_booking(user_token, booking_id, end_time=new_end.isoformat())
    assert resp2.status_code == 200
    assert resp2.json()["confirmed"] is False


def test_unconfirmed_overlap_allowed(user_token):
    # Book unconfirmed slot
    start = stockholm_dt(2030, 1, 12, 7)
    end = stockholm_dt(2030, 1, 12, 9)
    resp1 = create_booking(user_token, start, end, "unconfirmed1")
    assert resp1.json()["confirmed"] is False
    # Overlapping unconfirmed booking
    resp2 = create_booking(user_token, start, end, "unconfirmed2")
    assert resp2.status_code == 200
    assert resp2.json()["confirmed"] is False


def test_confirmed_overlap_not_allowed(boss_token):
    # Book confirmed slot
    start = stockholm_dt(2030, 1, 13, 10)
    end = stockholm_dt(2030, 1, 13, 12)
    resp1 = create_booking(boss_token, start, end, "confirmed1")
    assert resp1.json()["confirmed"] is True
    # Overlapping booking via POST should be auto-unconfirmed
    resp2 = create_booking(boss_token, start, end, "confirmed2")
    assert resp2.status_code == 200
    assert resp2.json()["confirmed"] is False


def test_confirmed_overlap_patch_not_allowed(boss_token):
    # Book two non-overlapping confirmed slots
    start1 = stockholm_dt(2030, 1, 15, 8)
    end1 = stockholm_dt(2030, 1, 15, 10)
    start2 = stockholm_dt(2030, 1, 15, 12)
    end2 = stockholm_dt(2030, 1, 15, 14)
    resp1 = create_booking(boss_token, start1, end1, "confirmed1")
    resp2 = create_booking(boss_token, start2, end2, "confirmed2")
    id1 = resp1.json()["booking_id"]
    id2 = resp2.json()["booking_id"]
    # Try to patch booking 2 to overlap with booking 1
    patch_resp = patch_booking(boss_token, id2, start_time=start1.isoformat(), end_time=end1.isoformat())
    assert patch_resp.status_code in (400, 422)


def test_unconfirmed_overlap_patch_allowed(user_token):
    # Book two non-overlapping unconfirmed slots
    start1 = stockholm_dt(2030, 1, 18, 7)
    end1 = stockholm_dt(2030, 1, 18, 9)
    start2 = stockholm_dt(2030, 1, 18, 19)
    end2 = stockholm_dt(2030, 1, 18, 21)
    resp1 = create_booking(user_token, start1, end1, "unconfirmed1")
    resp2 = create_booking(user_token, start2, end2, "unconfirmed2")
    assert resp1.json()["confirmed"] is False
    assert resp2.json()["confirmed"] is False

    # Patch booking 2 to overlap with booking 1
    id2 = resp2.json()["booking_id"]
    patch_resp = patch_booking(user_token, id2, start_time=start1.isoformat(), end_time=end1.isoformat())
    assert patch_resp.status_code == 200
    assert patch_resp.json()["confirmed"] is False


def test_confirmed_and_unconfirmed_patch_overlap_allowed(boss_token, user_token):
    # Confirmed booking by admin
    start1 = stockholm_dt(2030, 1, 19, 10)
    end1 = stockholm_dt(2030, 1, 19, 12)
    resp1 = create_booking(boss_token, start1, end1, "confirmed")
    assert resp1.json()["confirmed"] is True

    # Unconfirmed booking by user (not overlapping initially)
    start2 = stockholm_dt(2030, 1, 19, 7)
    end2 = stockholm_dt(2030, 1, 19, 8)
    resp2 = create_booking(user_token, start2, end2, "unconfirmed")
    assert resp2.json()["confirmed"] is False

    # Patch unconfirmed booking to overlap with confirmed
    booking_id = resp2.json()["booking_id"]
    new_end = stockholm_dt(2030, 1, 19, 11)  # Creates overlap
    patch_resp = patch_booking(user_token, booking_id, end_time=new_end.isoformat())
    assert patch_resp.status_code == 200
    assert patch_resp.json()["confirmed"] is False


def test_zero_length_booking_not_allowed(boss_token):
    # Try to create a zero-length booking
    start = stockholm_dt(2030, 1, 16, 10)
    end = stockholm_dt(2030, 1, 16, 10)
    resp = create_booking(boss_token, start, end, "zero length")
    assert resp.status_code in (400, 422)
    # Create a valid booking, then try to patch to zero-length
    valid_end = stockholm_dt(2030, 1, 16, 12)
    resp2 = create_booking(boss_token, start, valid_end, "valid")
    booking_id = resp2.json()["booking_id"]
    patch_resp = patch_booking(boss_token, booking_id, start_time=start.isoformat(), end_time=start.isoformat())
    assert patch_resp.status_code in (400, 422)


def test_confirmed_and_unconfirmed_overlap_allowed(boss_token, user_token):
    # Confirmed booking by admin
    start = stockholm_dt(2030, 1, 14, 10)
    end = stockholm_dt(2030, 1, 14, 12)
    resp1 = create_booking(boss_token, start, end, "confirmed")
    assert resp1.json()["confirmed"] is True
    # Overlapping unconfirmed booking by user
    start2 = stockholm_dt(2030, 1, 14, 7)
    end2 = stockholm_dt(2030, 1, 14, 11)
    resp2 = create_booking(user_token, start2, end2, "unconfirmed overlap")
    assert resp2.status_code == 200
    assert resp2.json()["confirmed"] is False


def test_end_before_start_not_allowed(boss_token):
    # Try to create a booking with end before start
    start = stockholm_dt(2030, 1, 17, 12)
    end = stockholm_dt(2030, 1, 17, 10)
    resp = create_booking(boss_token, start, end, "end before start")
    assert resp.status_code in (400, 422)
    # Create a valid booking, then try to patch to end before start
    valid_end = stockholm_dt(2030, 1, 17, 14)
    resp2 = create_booking(boss_token, start, valid_end, "valid")
    booking_id = resp2.json()["booking_id"]
    patch_resp = patch_booking(boss_token, booking_id, start_time=start.isoformat(), end_time=end.isoformat())
    assert patch_resp.status_code in (400, 422)


# New tests for council_id and personal bookings
def test_admin_can_select_any_council(boss_token, councils, non_user_council_id):
    start = stockholm_dt(2030, 3, 1, 10)
    end = stockholm_dt(2030, 3, 1, 12)

    # Admin should be able to book with any council
    resp = create_booking(boss_token, start, end, "admin council booking", council_id=non_user_council_id)
    assert resp.status_code == 200
    assert resp.json()["council_id"] == non_user_council_id


def test_user_can_select_own_council(user_token, user_council_id):
    start = stockholm_dt(2030, 3, 2, 10)
    end = stockholm_dt(2030, 3, 2, 12)

    # User should be able to book with their own council
    resp = create_booking(user_token, start, end, "user council booking", council_id=user_council_id)
    assert resp.status_code == 200
    assert resp.json()["council_id"] == user_council_id


def test_user_cannot_select_other_council(user_token, non_user_council_id):
    start = stockholm_dt(2030, 3, 3, 10)
    end = stockholm_dt(2030, 3, 3, 12)

    # User should not be able to book with a council they're not part of
    resp = create_booking(user_token, start, end, "unauthorized council booking", council_id=non_user_council_id)
    assert resp.status_code in (400, 403, 422)


def test_admin_edit_council(boss_token, councils):
    start = stockholm_dt(2030, 3, 4, 10)
    end = stockholm_dt(2030, 3, 4, 12)

    # Create booking with one council
    resp = create_booking(boss_token, start, end, "admin edit council", council_id=councils[0]["id"])
    booking_id = resp.json()["booking_id"]

    # Admin should be able to change the council
    resp2 = patch_booking(boss_token, booking_id, council_id=councils[1]["id"])
    assert resp2.status_code == 200
    assert resp2.json()["council_id"] == councils[1]["id"]


def test_user_cannot_edit_to_unauthorized_council(user_token, user_council_id, non_user_council_id):
    start = stockholm_dt(2030, 3, 5, 10)
    end = stockholm_dt(2030, 3, 5, 12)

    # Create booking with authorized council
    resp = create_booking(user_token, start, end, "user edit council", council_id=user_council_id)
    booking_id = resp.json()["booking_id"]

    # User should not be able to change to unauthorized council
    resp2 = patch_booking(user_token, booking_id, council_id=non_user_council_id)
    assert resp2.status_code in (400, 403, 422)


def test_personal_booking_creation_admin(boss_token):
    start = stockholm_dt(2030, 3, 6, 10)
    end = stockholm_dt(2030, 3, 6, 12)

    # Admin creates personal booking
    resp = create_booking(boss_token, start, end, "admin personal booking", personal=True, council_id=1)
    assert resp.status_code == 200
    data = resp.json()
    assert data["personal"] is True
    assert "council_id" in data


def test_personal_booking_creation_user(user_token, user_council_id):
    start = stockholm_dt(2030, 3, 7, 10)
    end = stockholm_dt(2030, 3, 7, 12)

    # User creates personal booking
    resp = create_booking(user_token, start, end, "user personal booking", personal=True, council_id=user_council_id)
    assert resp.status_code == 200
    data = resp.json()
    assert data["personal"] is True
    assert data["council_id"] == user_council_id


def test_edit_personal_flag(boss_token):
    start = stockholm_dt(2030, 3, 8, 10)
    end = stockholm_dt(2030, 3, 8, 12)

    # Create non-personal booking
    resp = create_booking(boss_token, start, end, "edit personal flag", personal=False, council_id=1)
    booking_id = resp.json()["booking_id"]

    # Edit to make it personal
    resp2 = patch_booking(boss_token, booking_id, personal=True)
    assert resp2.status_code == 200
    assert resp2.json()["personal"] is True

    # Edit back to non-personal
    resp3 = patch_booking(boss_token, booking_id, personal=False)
    assert resp3.status_code == 200
    assert resp3.json()["personal"] is False


def test_personal_booking_council_required(user_token):
    start = stockholm_dt(2030, 3, 9, 10)
    end = stockholm_dt(2030, 3, 9, 12)

    # Personal booking still requires valid council
    resp = create_booking(user_token, start, end, "personal without council", personal=True)
    assert resp.status_code in (400, 422)  # Either bad request or validation error
