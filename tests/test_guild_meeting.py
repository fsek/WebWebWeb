# type: ignore
from main import app
from .basic_factories import auth_headers


def test_get_guild_meeting_admin(client, admin_token):
    """Test that admin can view guild meeting info"""
    resp = client.get("/guild-meeting/", headers=auth_headers(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert "date_description_sv" in data
    assert "date_description_en" in data
    assert "description_sv" in data
    assert "description_en" in data
    assert data["id"] == 1


def test_get_guild_meeting_non_member(client, non_member_token):
    """Test that non-members can also view guild meeting info"""
    resp = client.get("/guild-meeting/", headers=auth_headers(non_member_token))
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert "date_description_sv" in data
    assert "date_description_en" in data
    assert "description_sv" in data
    assert "description_en" in data
    assert data["id"] == 1


def test_update_guild_meeting_admin(client, admin_token):
    """Test that admin can update guild meeting info"""
    # Update both fields
    update_data = {
        "date_description_sv": "Torsdag 15 januari 2030 kl 18:00",
        "date_description_en": "Thursday, January 15th, 2030 at 18:00",
        "description_sv": "Årsmöte med val och budgetgenomgång",
        "description_en": "Annual guild meeting with elections and budget review",
    }
    resp = client.patch("/guild-meeting/", json=update_data, headers=auth_headers(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["date_description_sv"] == update_data["date_description_sv"]
    assert data["date_description_en"] == update_data["date_description_en"]
    assert data["description_sv"] == update_data["description_sv"]
    assert data["description_en"] == update_data["description_en"]
    assert data["id"] == 1


def test_update_guild_meeting_empty_fields_admin(client, admin_token):
    """Test that admin can clear guild meeting fields"""
    update_data = {"date_description_sv": "", "date_description_en": "", "description_sv": "", "description_en": ""}
    resp = client.patch("/guild-meeting/", json=update_data, headers=auth_headers(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["date_description_sv"] == ""
    assert data["date_description_en"] == ""
    assert data["description_sv"] == ""
    assert data["description_en"] == ""


def test_update_guild_meeting_member_denied(client, member_token):
    """Test that regular members cannot update guild meeting info"""
    update_data = {
        "date_description_sv": "Otillåtet försök",
        "date_description_en": "Unauthorized update attempt",
        "description_sv": "Detta ska inte fungera",
        "description_en": "This should not work",
    }
    resp = client.patch("/guild-meeting/", json=update_data, headers=auth_headers(member_token))
    assert resp.status_code >= 400 and resp.status_code < 500


def test_update_guild_meeting_non_member_denied(client, non_member_token):
    """Test that non-members cannot update guild meeting info"""
    update_data = {
        "date_description_sv": "Otillåtet försök",
        "date_description_en": "Unauthorized update attempt",
        "description_sv": "Detta ska inte fungera",
        "description_en": "This should not work",
    }
    resp = client.patch("/guild-meeting/", json=update_data, headers=auth_headers(non_member_token))
    assert resp.status_code >= 400 and resp.status_code < 500


def test_guild_meeting_singleton_constraint(client, admin_token):
    """Test that the guild meeting maintains singleton behavior"""
    # Get the meeting multiple times to ensure it's always the same record
    resp1 = client.get("/guild-meeting/", headers=auth_headers(admin_token))
    resp2 = client.get("/guild-meeting/", headers=auth_headers(admin_token))
    resp3 = client.get("/guild-meeting/", headers=auth_headers(admin_token))

    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert resp3.status_code == 200

    # All should return the same ID
    assert resp1.json()["id"] == 1
    assert resp2.json()["id"] == 1
    assert resp3.json()["id"] == 1


def test_guild_meeting_persistence_across_updates(client, admin_token):
    """Test that guild meeting updates persist correctly"""
    # Set initial values
    initial_data = {
        "date_description_sv": "Initialdatum",
        "date_description_en": "Initial date",
        "description_sv": "Initial beskrivning",
        "description_en": "Initial description",
    }
    resp1 = client.patch("/guild-meeting/", json=initial_data, headers=auth_headers(admin_token))
    assert resp1.status_code == 200

    # Update only one field
    partial_update = {"date_description_sv": "Uppdaterat datum", "date_description_en": "Updated date"}
    resp2 = client.patch("/guild-meeting/", json=partial_update, headers=auth_headers(admin_token))
    assert resp2.status_code == 200

    # Verify the other fields persisted
    resp3 = client.get("/guild-meeting/", headers=auth_headers(admin_token))
    data = resp3.json()
    assert data["date_description_sv"] == "Uppdaterat datum"
    assert data["date_description_en"] == "Updated date"
    assert data["description_sv"] == "Initial beskrivning"  # Should remain unchanged
    assert data["description_en"] == "Initial description"  # Should remain unchanged

    # Update the other fields
    second_update = {"description_sv": "Uppdaterad beskrivning", "description_en": "Updated description"}
    resp4 = client.patch("/guild-meeting/", json=second_update, headers=auth_headers(admin_token))
    assert resp4.status_code == 200

    # Verify all fields are correct
    resp5 = client.get("/guild-meeting/", headers=auth_headers(admin_token))
    final_data = resp5.json()
    assert final_data["date_description_sv"] == "Uppdaterat datum"
    assert final_data["date_description_en"] == "Updated date"
    assert final_data["description_sv"] == "Uppdaterad beskrivning"
    assert final_data["description_en"] == "Updated description"
