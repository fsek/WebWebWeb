# type: ignore
from api_schemas.car_block_schema import CarBlockCreate
from main import app
from db_models.car_block_model import CarBlock_DB
from db_models.user_model import User_DB
from tests.test_car_bookings import stockholm_dt, create_booking, patch_booking
from tests.basic_factories import auth_headers


def block_user(db_session, user, reason="Test block", blocked_by=None):
    block = CarBlock_DB(user_id=user.id, reason=reason, blocked_by=blocked_by or user.id)
    db_session.add(block)
    db_session.commit()
    return block


def unblock_user(db_session, block):
    db_session.delete(block)
    db_session.commit()


def is_blocked(client, token, user_id):
    resp = client.get("/car/block/", headers=auth_headers(token))
    return any(b["user_id"] == user_id for b in resp.json())


def test_block_user_cannot_book(client, member_token, member_council_id, db_session, membered_user):
    block_user(db_session, membered_user)
    start = stockholm_dt(2030, 4, 1, 10)
    end = stockholm_dt(2030, 4, 1, 12)
    resp = create_booking(client, member_token, start, end, "blocked booking", council_id=member_council_id)
    assert resp.status_code == 403
    assert "blocked" in resp.text or "block" in resp.text


def test_block_user_cannot_edit(client, member_token, member_council_id, db_session, membered_user):
    block = block_user(db_session, membered_user)
    start = stockholm_dt(2030, 4, 2, 10)
    end = stockholm_dt(2030, 4, 2, 12)
    unblock_user(db_session, block)
    resp = create_booking(client, member_token, start, end, "edit test", council_id=member_council_id)
    booking_id = resp.json()["booking_id"]
    block_user(db_session, membered_user)
    resp2 = patch_booking(client, member_token, booking_id, description="should fail")
    assert resp2.status_code == 403
    assert "blocked" in resp2.text or "block" in resp2.text


def test_admin_can_block_and_unblock(client, admin_token, member_token, db_session, membered_user, admin_user):
    block = {"user_id": membered_user.id, "reason": "Violation", "blocked_by": admin_user.id}
    resp = client.post(
        "/car/block/",
        json=block,
        headers=auth_headers(admin_token),
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    # CarBlockRead fields expected
    assert data["user_id"] == membered_user.id
    assert data["reason"] == "Violation"
    assert "id" in data
    assert is_blocked(client, admin_token, membered_user.id)
    resp2 = client.delete(f"/car/block/{membered_user.id}", headers=auth_headers(admin_token))
    assert resp2.status_code in (200, 201, 204)
    data2 = resp2.json()
    # Should return the deleted CarBlockRead object
    assert data2["user_id"] == membered_user.id
    assert "id" in data2
    assert not is_blocked(client, admin_token, membered_user.id)


def test_list_blocks(client, admin_token, db_session, admin_user):
    block_user(db_session, admin_user, reason="Test list")
    resp = client.get("/car/block/", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    found = any(b["user_id"] == admin_user.id for b in resp.json())
    assert found


def test_double_block_fails(client, admin_token, db_session, membered_user, admin_user):
    block1 = {"user_id": membered_user.id, "reason": "First block", "blocked_by": admin_user.id}
    resp1 = client.post(
        "/car/block/",
        json=block1,
        headers=auth_headers(admin_token),
    )
    assert resp1.status_code in (200, 201)
    block2 = {"user_id": membered_user.id, "reason": "Second block", "blocked_by": admin_user.id}
    resp2 = client.post(
        "/car/block/",
        json=block2,
        headers=auth_headers(admin_token),
    )
    assert resp2.status_code >= 400 and resp2.status_code < 500


def test_unblock_nonblocked_user(client, admin_token, db_session, membered_user):
    resp = client.delete(f"/car/block/{membered_user.id}", headers=auth_headers(admin_token))
    assert resp.status_code >= 400 and resp.status_code < 500


def test_block_nonexistent_user(client, admin_token):
    resp = client.post(f"/car/block/999999", params={"reason": "No such user"}, headers=auth_headers(admin_token))
    assert resp.status_code >= 400 and resp.status_code < 500


def test_admin_not_blocked_can_book(client, admin_token, admin_council_id, db_session, admin_user):
    # Ensure not blocked
    blocks = db_session.query(CarBlock_DB).filter(CarBlock_DB.user_id == admin_user.id).all()
    for b in blocks:
        db_session.delete(b)
    db_session.commit()
    start = stockholm_dt(2030, 5, 1, 10)
    end = stockholm_dt(2030, 5, 1, 12)
    resp = create_booking(client, admin_token, start, end, "admin booking", council_id=admin_council_id)
    assert resp.status_code in (200, 201)
    assert resp.json()["confirmed"] is True


def test_blocked_user_cannot_delete_booking(client, member_token, member_council_id, db_session, membered_user):
    start = stockholm_dt(2030, 6, 1, 10)
    end = stockholm_dt(2030, 6, 1, 12)
    resp = create_booking(client, member_token, start, end, "delete test", council_id=member_council_id)
    booking_id = resp.json()["booking_id"]
    block_user(db_session, membered_user, blocked_by=membered_user.id)
    resp2 = client.delete(f"/car/{booking_id}", headers=auth_headers(member_token))
    assert resp2.status_code == 403
    assert "blocked" in resp2.text or "block" in resp2.text
