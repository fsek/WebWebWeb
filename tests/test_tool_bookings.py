# type: ignore
from datetime import datetime, timezone
from db_models.tool_booking_model import ToolBooking_DB
from .basic_factories import auth_headers


def dt(day, hour, minute=0):
    return datetime(2030, 1, day, hour, minute, tzinfo=timezone.utc)


def create_tool(client, token, **kwargs):
    body = {
        "name_sv": "Borrmaskin",
        "name_en": "Drill",
        "amount": 3,
        "description_sv": "En borrmaskin",
        "description_en": "A drill",
        **kwargs,
    }
    return client.post("/tools/", json=body, headers=auth_headers(token))


def create_tool_booking(client, token, tool_id, start, end, amount=1, description="example description"):
    body = {
        "tool_id": tool_id,
        "amount": amount,
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "description": description,
    }
    return client.post("/tool-booking/", json=body, headers=auth_headers(token))


def patch_tool_booking(client, token, booking_id, **kwargs):
    return client.patch(f"/tool-booking/{booking_id}", json=kwargs, headers=auth_headers(token))


# Testing tools


def test_admin_create_tool(client, admin_token):
    resp = create_tool(client, admin_token)
    assert resp.status_code in (200, 201), resp.text
    data = resp.json()
    assert data["name_sv"] == "Borrmaskin"
    assert data["name_en"] == "Drill"
    assert data["amount"] == 3
    assert data["description_en"] == "A drill"


def test_member_cannot_create_tool(client, member_token):
    resp = create_tool(client, member_token)
    assert resp.status_code == 403


def test_create_tool_duplicate_names(client, admin_token):
    assert create_tool(client, admin_token).status_code in (200, 201)

    resp = create_tool(client, admin_token, name_en="Other")
    assert resp.status_code == 400
    resp = create_tool(client, admin_token, name_sv="Annan")
    assert resp.status_code == 400


def test_create_tool_nonpositive_amount(client, admin_token):
    assert create_tool(client, admin_token, amount=0).status_code == 400
    assert create_tool(client, admin_token, amount=-1).status_code == 400


def test_member_can_view_tools(client, admin_token, member_token):
    tool_id = create_tool(client, admin_token).json()["id"]

    resp = client.get("/tools/", headers=auth_headers(member_token))
    assert resp.status_code == 200
    assert [tool["id"] for tool in resp.json()] == [tool_id]

    resp = client.get(f"/tools/{tool_id}", headers=auth_headers(member_token))
    assert resp.status_code == 200
    assert resp.json()["name_en"] == "Drill"


def test_unauthenticated_cannot_view_tools(client, admin_token):
    create_tool(client, admin_token)
    assert client.get("/tools/").status_code == 401


def test_get_nonexistent_tool(client, admin_token):
    assert client.get("/tools/999999", headers=auth_headers(admin_token)).status_code == 404


def test_update_tool(client, admin_token):
    tool_id = create_tool(client, admin_token).json()["id"]

    body = {"name_sv": "Såg", "name_en": "Saw", "amount": 5, "description_en": "A saw"}
    resp = client.patch(f"/tools/update_tool/{tool_id}", json=body, headers=auth_headers(admin_token))
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["name_en"] == "Saw"
    assert data["amount"] == 5
    assert data["description_en"] == "A saw"
    # Not given, so unchanged
    assert data["description_sv"] == "En borrmaskin"


def test_update_tool_conflicting_name(client, admin_token):
    create_tool(client, admin_token)
    other_id = create_tool(client, admin_token, name_sv="Såg", name_en="Saw").json()["id"]

    body = {"name_sv": "Borrmaskin", "name_en": "Saw", "amount": 1}
    resp = client.patch(f"/tools/update_tool/{other_id}", json=body, headers=auth_headers(admin_token))
    assert resp.status_code == 400

    body = {"name_sv": "Såg", "name_en": "Drill", "amount": 1}
    resp = client.patch(f"/tools/update_tool/{other_id}", json=body, headers=auth_headers(admin_token))
    assert resp.status_code == 400


def test_member_cannot_update_or_delete_tool(client, admin_token, member_token):
    tool_id = create_tool(client, admin_token).json()["id"]

    body = {"name_sv": "Såg", "name_en": "Saw", "amount": 5}
    resp = client.patch(f"/tools/update_tool/{tool_id}", json=body, headers=auth_headers(member_token))
    assert resp.status_code == 403
    assert client.delete(f"/tools/{tool_id}", headers=auth_headers(member_token)).status_code == 403


def test_delete_tool_deletes_bookings(client, admin_token, db_session):
    tool_id = create_tool(client, admin_token).json()["id"]
    booking_id = create_tool_booking(client, admin_token, tool_id, dt(8, 10), dt(8, 12)).json()["id"]

    resp = client.delete(f"/tools/{tool_id}", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert client.get(f"/tools/{tool_id}", headers=auth_headers(admin_token)).status_code == 404
    assert db_session.query(ToolBooking_DB).filter_by(id=booking_id).one_or_none() is None


# Test tool bookings


def test_admin_create_tool_booking(client, admin_token, admin_user):
    tool_id = create_tool(client, admin_token).json()["id"]

    resp = create_tool_booking(client, admin_token, tool_id, dt(8, 10), dt(8, 12), amount=2)
    assert resp.status_code in (200, 201), resp.text
    data = resp.json()
    assert data["tool"]["id"] == tool_id
    assert data["amount"] == 2
    assert data["user"]["id"] == admin_user.id
    assert data["description"] == "example description"


def test_member_cannot_create_tool_booking(client, admin_token, member_token):
    tool_id = create_tool(client, admin_token).json()["id"]
    resp = create_tool_booking(client, member_token, tool_id, dt(8, 10), dt(8, 12))
    assert resp.status_code == 403


def test_create_tool_booking_invalid(client, admin_token):
    tool_id = create_tool(client, admin_token).json()["id"]

    # Nonexistent tool
    assert create_tool_booking(client, admin_token, 999999, dt(8, 10), dt(8, 12)).status_code == 404
    # Nonpositive amount
    assert create_tool_booking(client, admin_token, tool_id, dt(8, 10), dt(8, 12), amount=0).status_code == 400
    # End before start
    assert create_tool_booking(client, admin_token, tool_id, dt(8, 12), dt(8, 10)).status_code == 400
    # End equal to start
    assert create_tool_booking(client, admin_token, tool_id, dt(8, 10), dt(8, 10)).status_code == 400
    # More than exists
    assert create_tool_booking(client, admin_token, tool_id, dt(8, 10), dt(8, 12), amount=4).status_code == 400


def test_create_tool_booking_overbooking(client, admin_token):
    tool_id = create_tool(client, admin_token, amount=3).json()["id"]

    assert create_tool_booking(client, admin_token, tool_id, dt(8, 10), dt(8, 14), amount=2).status_code == 200
    # Only 1 left between 10 and 14
    assert create_tool_booking(client, admin_token, tool_id, dt(8, 12), dt(8, 16), amount=2).status_code == 400
    assert create_tool_booking(client, admin_token, tool_id, dt(8, 12), dt(8, 16), amount=1).status_code == 200
    # Now fully booked 12-14
    assert create_tool_booking(client, admin_token, tool_id, dt(8, 13), dt(8, 13, 30)).status_code == 400
    # Bookings touching at the edges do not overlap
    assert create_tool_booking(client, admin_token, tool_id, dt(8, 8), dt(8, 10), amount=3).status_code == 200
    assert create_tool_booking(client, admin_token, tool_id, dt(8, 16), dt(8, 18), amount=3).status_code == 200


def test_create_tool_booking_non_overlapping_existing(client, admin_token):
    # Two existing bookings overlap the new one but not each other, so the peak is 2, not 4
    tool_id = create_tool(client, admin_token, amount=3).json()["id"]

    assert create_tool_booking(client, admin_token, tool_id, dt(8, 8), dt(8, 10), amount=2).status_code == 200
    assert create_tool_booking(client, admin_token, tool_id, dt(8, 11), dt(8, 13), amount=2).status_code == 200
    assert create_tool_booking(client, admin_token, tool_id, dt(8, 9), dt(8, 12), amount=1).status_code == 200
    assert create_tool_booking(client, admin_token, tool_id, dt(8, 9), dt(8, 12), amount=1).status_code == 400


def test_bookings_on_different_tools_do_not_conflict(client, admin_token):
    drill_id = create_tool(client, admin_token, amount=1).json()["id"]
    saw_id = create_tool(client, admin_token, name_sv="Såg", name_en="Saw", amount=1).json()["id"]

    assert create_tool_booking(client, admin_token, drill_id, dt(8, 10), dt(8, 12)).status_code == 200
    assert create_tool_booking(client, admin_token, saw_id, dt(8, 10), dt(8, 12)).status_code == 200


def test_get_tool_booking(client, admin_token, member_token, admin_user):
    tool_id = create_tool(client, admin_token).json()["id"]
    booking_id = create_tool_booking(client, admin_token, tool_id, dt(8, 10), dt(8, 12), amount=2).json()["id"]

    resp = client.get(f"/tool-booking/get_booking/{booking_id}", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert resp.json()["user"]["id"] == admin_user.id
    assert resp.json()["amount"] == 2

    # Members can't see who booked
    resp = client.get(f"/tool-booking/get_booking/{booking_id}", headers=auth_headers(member_token))
    assert resp.status_code == 403

    resp = client.get(f"/tool-booking/get_simple_booking/{booking_id}", headers=auth_headers(member_token))
    assert resp.status_code == 200
    data = resp.json()
    assert "user" not in data
    assert data["amount"] == 2
    assert data["tool"]["id"] == tool_id

    resp = client.get("/tool-booking/get_simple_booking/999999", headers=auth_headers(member_token))
    assert resp.status_code == 404


def test_get_all_tool_bookings(client, admin_token, member_token):
    tool_id = create_tool(client, admin_token).json()["id"]
    create_tool_booking(client, admin_token, tool_id, dt(8, 10), dt(8, 12))
    create_tool_booking(client, admin_token, tool_id, dt(9, 10), dt(9, 12))

    resp = client.get("/tool-booking/get_all", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2
    assert all("user" in booking for booking in resp.json())

    assert client.get("/tool-booking/get_all", headers=auth_headers(member_token)).status_code == 403

    resp = client.get("/tool-booking/get_simple_all", headers=auth_headers(member_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2
    assert all("user" not in booking for booking in resp.json())

    assert client.get("/tool-booking/get_simple_all").status_code == 401


def test_get_tool_bookings_between_times(client, admin_token, member_token):
    tool_id = create_tool(client, admin_token).json()["id"]
    inside = create_tool_booking(client, admin_token, tool_id, dt(8, 11), dt(8, 12)).json()["id"]
    over_start = create_tool_booking(client, admin_token, tool_id, dt(8, 9), dt(8, 11)).json()["id"]
    over_end = create_tool_booking(client, admin_token, tool_id, dt(8, 13), dt(8, 15)).json()["id"]
    around = create_tool_booking(client, admin_token, tool_id, dt(8, 8), dt(8, 16)).json()["id"]
    # Outside or only touching the edges
    create_tool_booking(client, admin_token, tool_id, dt(8, 8), dt(8, 10))
    create_tool_booking(client, admin_token, tool_id, dt(8, 14), dt(8, 16))
    create_tool_booking(client, admin_token, tool_id, dt(9, 10), dt(9, 14))

    params = {"start_time": dt(8, 10).isoformat(), "end_time": dt(8, 14).isoformat()}
    expected = {inside, over_start, over_end, around}

    resp = client.get("/tool-booking/get_between_times", params=params, headers=auth_headers(admin_token))
    assert resp.status_code == 200, resp.text
    assert {booking["id"] for booking in resp.json()} == expected

    resp = client.get("/tool-booking/get_simple_between_times", params=params, headers=auth_headers(member_token))
    assert resp.status_code == 200, resp.text
    assert {booking["id"] for booking in resp.json()} == expected

    resp = client.get("/tool-booking/get_between_times", params=params, headers=auth_headers(member_token))
    assert resp.status_code == 403


def test_get_tool_bookings_by_tool(client, admin_token, member_token):
    drill_id = create_tool(client, admin_token).json()["id"]
    saw_id = create_tool(client, admin_token, name_sv="Såg", name_en="Saw").json()["id"]
    drill_booking = create_tool_booking(client, admin_token, drill_id, dt(8, 10), dt(8, 12)).json()["id"]
    create_tool_booking(client, admin_token, saw_id, dt(8, 10), dt(8, 12))

    resp = client.get("/tool-booking/get_by_tool/", params={"tool_id": drill_id}, headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert [booking["id"] for booking in resp.json()] == [drill_booking]

    resp = client.get(
        "/tool-booking/get_simple_by_tool/", params={"tool_id": drill_id}, headers=auth_headers(member_token)
    )
    assert resp.status_code == 200
    assert [booking["id"] for booking in resp.json()] == [drill_booking]

    resp = client.get("/tool-booking/get_by_tool/", params={"tool_id": drill_id}, headers=auth_headers(member_token))
    assert resp.status_code == 403

    resp = client.get("/tool-booking/get_by_tool/", params={"tool_id": 999999}, headers=auth_headers(admin_token))
    assert resp.status_code == 404


def test_delete_tool_booking(client, admin_token, member_token):
    tool_id = create_tool(client, admin_token, amount=1).json()["id"]
    booking_id = create_tool_booking(client, admin_token, tool_id, dt(8, 10), dt(8, 12)).json()["id"]

    assert client.delete(f"/tool-booking/{booking_id}", headers=auth_headers(member_token)).status_code == 403

    resp = client.delete(f"/tool-booking/{booking_id}", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    assert client.get(f"/tool-booking/get_booking/{booking_id}", headers=auth_headers(admin_token)).status_code == 404
    assert client.delete(f"/tool-booking/{booking_id}", headers=auth_headers(admin_token)).status_code == 404

    # The tool is free again
    assert create_tool_booking(client, admin_token, tool_id, dt(8, 10), dt(8, 12)).status_code == 200


def test_update_tool_booking(client, admin_token):
    tool_id = create_tool(client, admin_token, amount=3).json()["id"]
    booking_id = create_tool_booking(client, admin_token, tool_id, dt(8, 10), dt(8, 12)).json()["id"]

    resp = patch_tool_booking(
        client, admin_token, booking_id, amount=3, start_time=dt(8, 9).isoformat(), end_time=dt(8, 13).isoformat()
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["amount"] == 3
    assert datetime.fromisoformat(data["start_time"]) == dt(8, 9)
    assert datetime.fromisoformat(data["end_time"]) == dt(8, 13)
    assert data["description"] == "example description"


def test_update_tool_booking_invalid(client, admin_token, member_token):
    tool_id = create_tool(client, admin_token).json()["id"]
    booking_id = create_tool_booking(client, admin_token, tool_id, dt(8, 10), dt(8, 12)).json()["id"]

    assert patch_tool_booking(client, admin_token, 999999, amount=1).status_code == 404
    assert patch_tool_booking(client, admin_token, booking_id, amount=0).status_code == 400
    assert patch_tool_booking(client, admin_token, booking_id, end_time=dt(8, 9).isoformat()).status_code == 400
    assert patch_tool_booking(client, admin_token, booking_id, start_time=dt(8, 12).isoformat()).status_code == 400
    assert patch_tool_booking(client, member_token, booking_id, amount=1).status_code == 403


def test_update_tool_booking_amount_overbooking(client, admin_token):
    tool_id = create_tool(client, admin_token, amount=3).json()["id"]
    create_tool_booking(client, admin_token, tool_id, dt(8, 10), dt(8, 12), amount=2)
    booking_id = create_tool_booking(client, admin_token, tool_id, dt(8, 11), dt(8, 13)).json()["id"]

    assert patch_tool_booking(client, admin_token, booking_id, amount=2).status_code == 400
    # The booking itself is not counted as overlapping
    assert patch_tool_booking(client, admin_token, booking_id, amount=1).status_code == 200


def test_update_tool_booking_time_overbooking(client, admin_token):
    tool_id = create_tool(client, admin_token, amount=2).json()["id"]
    create_tool_booking(client, admin_token, tool_id, dt(8, 10), dt(8, 12), amount=2)
    booking_id = create_tool_booking(client, admin_token, tool_id, dt(8, 14), dt(8, 16), amount=1).json()["id"]

    # Moving into a fully booked time without changing the amount
    resp = patch_tool_booking(
        client, admin_token, booking_id, start_time=dt(8, 11).isoformat(), end_time=dt(8, 13).isoformat()
    )
    assert resp.status_code == 400
    resp = patch_tool_booking(client, admin_token, booking_id, start_time=dt(8, 11).isoformat())
    assert resp.status_code == 400

    # Moving to a free time is fine
    resp = patch_tool_booking(client, admin_token, booking_id, start_time=dt(8, 12).isoformat())
    assert resp.status_code == 200, resp.text


def test_update_tool_booking_description(client, admin_token):
    tool_id = create_tool(client, admin_token).json()["id"]
    booking_id = create_tool_booking(client, admin_token, tool_id, dt(8, 10), dt(8, 12)).json()["id"]

    resp = patch_tool_booking(client, admin_token, booking_id, description="new description")
    assert resp.status_code == 200
    assert resp.json()["description"] == "new description"

    # Not given, so unchanged
    resp = patch_tool_booking(client, admin_token, booking_id, amount=2)
    assert resp.status_code == 200
    assert resp.json()["description"] == "new description"

    resp = patch_tool_booking(client, admin_token, booking_id, description="")
    assert resp.status_code == 200
    assert resp.json()["description"] == ""

    resp = patch_tool_booking(client, admin_token, booking_id, description=None)
    assert resp.status_code == 200
    assert resp.json()["description"] is None


def test_deleting_user_deletes_tool_bookings(client, admin_token, admin_user, db_session):
    tool_id = create_tool(client, admin_token).json()["id"]
    booking_id = create_tool_booking(client, admin_token, tool_id, dt(8, 10), dt(8, 12)).json()["id"]

    db_session.delete(admin_user)
    db_session.commit()
    db_session.expire_all()

    assert db_session.query(ToolBooking_DB).filter_by(id=booking_id).one_or_none() is None
