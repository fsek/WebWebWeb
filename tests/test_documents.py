# type: ignore
from .basic_factories import auth_headers
import pytest


def create_document_object(
    client,
    token,
    example_file,
    title="Test document",
    category="Test category",
    is_private=False,
):
    data = {
        "title": title,
        "category": category,
        "is_private": str(is_private).lower(),
    }
    files = {
        "file": example_file,
    }
    return client.post(
        "/document/",
        data=data,
        files=files,
        headers=auth_headers(token),
    )


def update_document_object(
    client, token, document_id, title="Test document", category="Test category", is_private=False
):
    data = {
        "title": title,
        "category": category,
        "is_private": str(is_private).lower(),
    }
    return client.patch(
        f"/document/patch_document/{document_id}",
        json=data,
        headers=auth_headers(token),
    )


def test_create_document(client, admin_token, example_file):
    """Test that an admin can create a document"""
    response = create_document_object(
        client,
        admin_token,
        example_file,
    )
    assert response.status_code in [200, 201]
    assert response.json()["title"] == "Test document"
    assert response.json()["category"] == "Test category"
    assert response.json()["is_private"] is False


def test_patch_document(client, admin_token, example_file):
    """Test that an admin can update a document"""
    # First, create a document to update
    create_response = create_document_object(
        client,
        admin_token,
        example_file,
    )
    assert create_response.status_code in [200, 201]
    document_id = create_response.json()["id"]

    # Now, update the document
    update_response = update_document_object(
        client, admin_token, document_id, title="Updated document", category="Updated category", is_private=True
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated document"
    assert update_response.json()["category"] == "Updated category"
    assert update_response.json()["is_private"] is True


def test_unauthorized_can_access_public_document(client, admin_token, example_file):
    """Test that an unauthorized user can access a public document"""
    # First, create a public document
    create_response = create_document_object(
        client,
        admin_token,
        example_file,
        is_private=False,
    )
    assert create_response.status_code in [200, 201]
    document_id = create_response.json()["id"]

    # Now, try to access the document with a different user (unauthorized)
    unauthorized_response = client.get(f"/document/document_data/{document_id}")
    assert unauthorized_response.status_code == 200
    assert unauthorized_response.json()["is_private"] is False


def test_unauthorized_cannot_access_private_document(client, admin_token, example_file):
    """Test that an unauthorized user cannot access a private document"""
    # Create a private document
    create_response = create_document_object(
        client,
        admin_token,
        example_file,
        is_private=True,
    )
    assert create_response.status_code in [200, 201]
    document_id = create_response.json()["id"]

    # Try to access as unauthorized user
    unauthorized_response = client.get(f"/document/document_data/{document_id}")
    assert unauthorized_response.status_code == 401


def test_unauthorized_cannot_upload_document(client, example_file):
    """Test that an unauthorized user cannot upload a document"""
    data = {
        "title": "Unauthorized doc",
        "category": "Test",
        "is_private": "false",
    }
    files = {
        "file": example_file,
    }
    response = client.post("/document/", data=data, files=files)
    assert response.status_code == 401 or response.status_code == 403


def test_unauthorized_cannot_patch_document(client, admin_token, example_file):
    """Test that an unauthorized user cannot patch a document"""
    create_response = create_document_object(
        client,
        admin_token,
        example_file,
    )
    document_id = create_response.json()["id"]
    data = {
        "title": "Should not update",
        "category": "Should not update",
        "is_private": False,
    }
    response = client.patch(f"/document/patch_document/{document_id}", json=data)
    assert response.status_code == 401 or response.status_code == 403


def test_member_can_access_public_document(client, member_token, admin_token, example_file):
    """Test that a member can access a public document"""
    create_response = create_document_object(
        client,
        admin_token,
        example_file,
        is_private=False,
    )
    document_id = create_response.json()["id"]
    response = client.get(f"/document/document_data/{document_id}", headers=auth_headers(member_token))
    assert response.status_code == 200
    assert response.json()["is_private"] is False


def test_member_can_access_private_document(client, member_token, admin_token, example_file):
    """Test that a member can access a private document"""
    create_response = create_document_object(
        client,
        admin_token,
        example_file,
        is_private=True,
    )
    document_id = create_response.json()["id"]
    response = client.get(f"/document/document_data/{document_id}", headers=auth_headers(member_token))
    assert response.status_code == 200
    assert response.json()["is_private"] is True


def test_member_cannot_upload_document(client, member_token, example_file):
    """Test that a member cannot upload a document"""
    data = {
        "title": "Member doc",
        "category": "Test",
        "is_private": "false",
    }
    files = {
        "file": example_file,
    }
    response = client.post("/document/", data=data, files=files, headers=auth_headers(member_token))
    assert response.status_code == 403


def test_member_cannot_patch_document(client, member_token, admin_token, example_file):
    """Test that a member cannot patch a document"""
    create_response = create_document_object(
        client,
        admin_token,
        example_file,
    )
    document_id = create_response.json()["id"]
    data = {
        "title": "Should not update",
        "category": "Should not update",
        "is_private": False,
    }
    response = client.patch(f"/document/patch_document/{document_id}", json=data, headers=auth_headers(member_token))
    assert response.status_code == 403


def test_admin_can_access_private_document(client, admin_token, example_file):
    """Test that an admin can access a private document"""
    create_response = create_document_object(
        client,
        admin_token,
        example_file,
        is_private=True,
    )
    document_id = create_response.json()["id"]
    response = client.get(f"/document/document_data/{document_id}", headers=auth_headers(admin_token))
    assert response.status_code == 200
    assert response.json()["is_private"] is True
