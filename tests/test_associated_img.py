# type: ignore
import asyncio
import os

from database import redis_client
from db_models.associated_img_model import AssociatedImg_DB

from .basic_factories import (
    auth_headers,
    create_associated_image,
    create_course,
    create_program,
    create_program_year,
    create_specialisation,
)


def _create_program_for_image_tests(client, admin_token):
    response = create_program(client, token=admin_token)
    assert response.status_code in (200, 201), response.text
    return response.json()["program_id"]


def _upload_program_image_and_get_img_id(client, admin_token, program_id, example_image_file):
    upload_response = create_associated_image(
        client,
        token=admin_token,
        association_type="program",
        association_id=program_id,
        file=example_image_file,
    )
    assert upload_response.status_code in (200, 201), upload_response.text

    program_response = client.get(f"/programs/{program_id}")
    assert program_response.status_code == 200, program_response.text
    img_id = program_response.json()["associated_img_id"]
    assert img_id is not None
    return img_id


def _create_plugg_entities_for_image_tests(client, admin_token):
    program_response = create_program(client, token=admin_token)
    assert program_response.status_code in (200, 201), program_response.text
    program_id = program_response.json()["program_id"]

    program_year_response = create_program_year(client, token=admin_token, program_id=program_id)
    assert program_year_response.status_code in (200, 201), program_year_response.text
    program_year_id = program_year_response.json()["program_year_id"]

    specialisation_response = create_specialisation(client, token=admin_token, program_id=program_id)
    assert specialisation_response.status_code in (200, 201), specialisation_response.text
    specialisation_id = specialisation_response.json()["specialisation_id"]

    course_response = create_course(
        client,
        token=admin_token,
        program_year_ids=[program_year_id],
        specialisation_ids=[specialisation_id],
    )
    assert course_response.status_code in (200, 201), course_response.text
    course_id = course_response.json()["course_id"]

    return {
        "program_id": program_id,
        "program_year_id": program_year_id,
        "specialisation_id": specialisation_id,
        "course_id": course_id,
    }


def _get_img_id_from_entity(client, association_type, association_id):
    endpoint_by_type = {
        "program": f"/programs/{association_id}",
        "program_year": f"/program-years/{association_id}",
        "course": f"/courses/{association_id}",
        "specialisation": f"/specialisations/{association_id}",
    }

    response = client.get(endpoint_by_type[association_type])
    assert response.status_code == 200, response.text
    return response.json()["associated_img_id"]


def test_admin_can_upload_associated_image(client, admin_token, db_session, example_image_file):
    program_id = _create_program_for_image_tests(client, admin_token)

    img_id = _upload_program_image_and_get_img_id(client, admin_token, program_id, example_image_file)

    image_in_db = db_session.query(AssociatedImg_DB).filter_by(associated_img_id=img_id).one_or_none()
    assert image_in_db is not None
    assert os.path.exists(image_in_db.path)


def test_unauthorized_cannot_upload_associated_image(client, admin_token, example_image_file):
    program_id = _create_program_for_image_tests(client, admin_token)

    response = create_associated_image(
        client,
        token=None,
        association_type="program",
        association_id=program_id,
        file=example_image_file,
    )
    assert response.status_code in (401, 403)


def test_member_cannot_upload_associated_image(client, admin_token, member_token, example_image_file):
    program_id = _create_program_for_image_tests(client, admin_token)

    response = create_associated_image(
        client,
        token=member_token,
        association_type="program",
        association_id=program_id,
        file=example_image_file,
    )
    assert response.status_code == 403


def test_upload_associated_image_requires_existing_entity(client, admin_token, example_image_file):
    response = create_associated_image(
        client,
        token=admin_token,
        association_type="program",
        association_id=999999,
        file=example_image_file,
    )
    assert response.status_code == 404


def test_upload_associated_image_rejects_invalid_extension(client, admin_token):
    program_id = _create_program_for_image_tests(client, admin_token)

    bad_file = ("not_an_image.txt", b"this is not an image", "text/plain")
    response = create_associated_image(
        client,
        token=admin_token,
        association_type="program",
        association_id=program_id,
        file=bad_file,
    )
    assert response.status_code == 400


def test_upload_associated_image_rejects_invalid_type(client, admin_token, example_image_file):
    program_id = _create_program_for_image_tests(client, admin_token)

    response = create_associated_image(
        client,
        token=admin_token,
        association_type="invalid_type",
        association_id=program_id,
        file=example_image_file,
    )
    assert response.status_code in (400, 422)


def test_get_associated_image_stream_success(client, admin_token, example_image_file):
    program_id = _create_program_for_image_tests(client, admin_token)
    img_id = _upload_program_image_and_get_img_id(client, admin_token, program_id, example_image_file)

    response = client.get(f"/associated-img/stream/{img_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_get_associated_image_internal_redirect_success(client, admin_token, db_session, example_image_file):
    program_id = _create_program_for_image_tests(client, admin_token)
    img_id = _upload_program_image_and_get_img_id(client, admin_token, program_id, example_image_file)

    image_in_db = db_session.query(AssociatedImg_DB).filter_by(associated_img_id=img_id).one_or_none()
    assert image_in_db is not None

    assert redis_client is not None
    asyncio.run(redis_client.set(f"img:{img_id}:path", image_in_db.path))

    response = client.get(f"/associated-img/images/{img_id}/small")
    assert response.status_code == 200
    assert response.headers["x-accel-redirect"] == f"/internal/200x200/{image_in_db.path.lstrip('/')}"


def test_admin_can_delete_associated_image(client, admin_token, db_session, example_image_file):
    program_id = _create_program_for_image_tests(client, admin_token)
    img_id = _upload_program_image_and_get_img_id(client, admin_token, program_id, example_image_file)

    delete_response = client.delete(f"/associated-img/{img_id}", headers=auth_headers(admin_token))
    assert delete_response.status_code == 200

    image_in_db = db_session.query(AssociatedImg_DB).filter_by(associated_img_id=img_id).one_or_none()
    assert image_in_db is None

    program_response = client.get(f"/programs/{program_id}")
    assert program_response.status_code == 200
    assert program_response.json()["associated_img_id"] is None


def test_member_cannot_delete_associated_image(client, admin_token, member_token, example_image_file):
    program_id = _create_program_for_image_tests(client, admin_token)
    img_id = _upload_program_image_and_get_img_id(client, admin_token, program_id, example_image_file)

    response = client.delete(f"/associated-img/{img_id}", headers=auth_headers(member_token))
    assert response.status_code == 403


def test_associated_image_linking_works_for_all_association_types(client, admin_token, db_session, example_image_file):
    ids = _create_plugg_entities_for_image_tests(client, admin_token)

    for association_type in ("program", "program_year", "course", "specialisation"):
        association_id = ids[f"{association_type}_id"]

        upload_response = create_associated_image(
            client,
            token=admin_token,
            association_type=association_type,
            association_id=association_id,
            file=example_image_file,
        )
        assert upload_response.status_code in (200, 201), upload_response.text

        img_id = _get_img_id_from_entity(client, association_type, association_id)
        assert img_id is not None

        image_in_db = db_session.query(AssociatedImg_DB).filter_by(associated_img_id=img_id).one_or_none()
        assert image_in_db is not None


def test_deleting_associated_image_unlinks_all_association_types(client, admin_token, example_image_file):
    ids = _create_plugg_entities_for_image_tests(client, admin_token)

    for association_type in ("program", "program_year", "course", "specialisation"):
        association_id = ids[f"{association_type}_id"]

        upload_response = create_associated_image(
            client,
            token=admin_token,
            association_type=association_type,
            association_id=association_id,
            file=example_image_file,
        )
        assert upload_response.status_code in (200, 201), upload_response.text

        img_id = _get_img_id_from_entity(client, association_type, association_id)
        assert img_id is not None

        delete_response = client.delete(f"/associated-img/{img_id}", headers=auth_headers(admin_token))
        assert delete_response.status_code == 200, delete_response.text

        assert _get_img_id_from_entity(client, association_type, association_id) is None
