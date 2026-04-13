# type: ignore
import os
import pytest

from .basic_factories import (
    auth_headers,
    course_document_data_factory,
    create_course_document,
)


@pytest.fixture
def plugg_course_id(db_session):
    from db_models.course_model import Course_DB

    course = Course_DB(
        title="Grundkurs i programmering",
        course_code="EDAA01",
        description="Test course for course-document tests",
    )
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)
    return course.course_id


def test_create_course_document_success(client, admin_token, plugg_course_id, example_file):
    payload = course_document_data_factory(course_id=plugg_course_id)
    response = create_course_document(
        client,
        token=admin_token,
        file=example_file,
        **payload,
    )

    assert response.status_code in (200, 201), response.text
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["author"] == payload["author"]
    assert data["category"] == payload["category"]
    assert data["course_id"] == plugg_course_id
    assert data["file_name"].endswith(".pdf")


def test_patch_course_document_success(client, admin_token, plugg_course_id, example_file):
    create_response = create_course_document(
        client,
        token=admin_token,
        file=example_file,
        **course_document_data_factory(course_id=plugg_course_id),
    )
    assert create_response.status_code in (200, 201), create_response.text
    document_id = create_response.json()["course_document_id"]

    patch_data = {
        "title": "Updated notes",
        "file_name": "updated_notes.pdf",
        "author": "Updated author",
        "category": "Summary",
        "sub_category": "by author 2",
    }

    patch_response = client.patch(
        f"/course-documents/{document_id}",
        json=patch_data,
        headers=auth_headers(admin_token),
    )

    assert patch_response.status_code == 200, patch_response.text
    data = patch_response.json()
    assert data["title"] == "Updated notes"
    assert data["file_name"] == "updated_notes.pdf"
    assert data["author"] == "Updated author"
    assert data["category"] == "Summary"


def test_get_course_document_by_id_public(client, admin_token, plugg_course_id, example_file):
    create_response = create_course_document(
        client,
        token=admin_token,
        file=example_file,
        **course_document_data_factory(course_id=plugg_course_id),
    )
    assert create_response.status_code in (200, 201), create_response.text
    document_id = create_response.json()["course_document_id"]

    response = client.get(f"/course-documents/{document_id}")
    assert response.status_code == 200
    assert response.json()["course_document_id"] == document_id


def test_get_all_course_documents_public(client, admin_token, plugg_course_id, example_file):
    create_response = create_course_document(
        client,
        token=admin_token,
        file=example_file,
        **course_document_data_factory(course_id=plugg_course_id),
    )
    assert create_response.status_code in (200, 201), create_response.text
    document_id = create_response.json()["course_document_id"]

    response = client.get("/course-documents/")
    assert response.status_code == 200
    assert any(document["course_document_id"] == document_id for document in response.json())


def test_create_course_document_requires_existing_course(client, admin_token, example_file):
    response = create_course_document(
        client,
        token=admin_token,
        file=example_file,
        **course_document_data_factory(course_id=999999),
    )

    assert response.status_code == 400


def test_unauthorized_cannot_upload_course_document(client, plugg_course_id, example_file):
    response = create_course_document(
        client,
        token=None,
        file=example_file,
        **course_document_data_factory(course_id=plugg_course_id),
    )

    assert response.status_code in (401, 403)


def test_member_cannot_upload_course_document(
    client,
    member_token,
    plugg_course_id,
    example_file,
):
    response = create_course_document(
        client,
        token=member_token,
        file=example_file,
        **course_document_data_factory(course_id=plugg_course_id),
    )

    assert response.status_code == 403


def test_unauthorized_cannot_patch_course_document(
    client,
    admin_token,
    plugg_course_id,
    example_file,
):
    create_response = create_course_document(
        client,
        token=admin_token,
        file=example_file,
        **course_document_data_factory(course_id=plugg_course_id),
    )
    assert create_response.status_code in (200, 201), create_response.text
    document_id = create_response.json()["course_document_id"]

    patch_data = {
        "title": "Forbidden patch",
        "file_name": "forbidden.pdf",
        "author": "Unauthorized",
        "category": "Other",
        "sub_category": None,
    }
    response = client.patch(f"/course-documents/{document_id}", json=patch_data)

    assert response.status_code in (401, 403)


def test_member_cannot_patch_course_document(client, member_token, admin_token, plugg_course_id, example_file):
    create_response = create_course_document(
        client,
        token=admin_token,
        file=example_file,
        **course_document_data_factory(course_id=plugg_course_id),
    )
    assert create_response.status_code in (200, 201), create_response.text
    document_id = create_response.json()["course_document_id"]

    patch_data = {
        "title": "Forbidden patch",
        "file_name": "forbidden.pdf",
        "author": "Member",
        "category": "Other",
        "sub_category": None,
    }
    response = client.patch(
        f"/course-documents/{document_id}",
        json=patch_data,
        headers=auth_headers(member_token),
    )

    assert response.status_code == 403


def test_delete_course_document_success(client, admin_token, plugg_course_id, example_file):
    create_response = create_course_document(
        client,
        token=admin_token,
        file=example_file,
        **course_document_data_factory(course_id=plugg_course_id),
    )
    assert create_response.status_code in (200, 201), create_response.text
    document_id = create_response.json()["course_document_id"]

    get_response = client.get(f"/course-documents/{document_id}")
    assert get_response.status_code == 200

    delete_response = client.delete(f"/course-documents/{document_id}", headers=auth_headers(admin_token))
    assert delete_response.status_code == 200

    get_response = client.get(f"/course-documents/{document_id}")
    assert get_response.status_code == 404


def test_member_cannot_delete_course_document(
    client,
    member_token,
    admin_token,
    plugg_course_id,
    example_file,
):
    create_response = create_course_document(
        client,
        token=admin_token,
        file=example_file,
        **course_document_data_factory(course_id=plugg_course_id),
    )
    assert create_response.status_code in (200, 201), create_response.text
    document_id = create_response.json()["course_document_id"]

    response = client.delete(f"/course-documents/{document_id}", headers=auth_headers(member_token))
    assert response.status_code == 403
