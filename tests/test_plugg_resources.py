# type: ignore
import pytest

from .basic_factories import (
    auth_headers,
    course_data_factory,
    create_course,
    create_program,
    create_program_year,
    create_specialisation,
    program_data_factory,
    program_year_data_factory,
    specialisation_data_factory,
)


@pytest.fixture
def base_program(client, admin_token):
    response = create_program(client, token=admin_token)
    assert response.status_code in (200, 201), response.text
    return response.json()


@pytest.fixture
def plugg_relationship_ids(client, admin_token, base_program):
    program_id = base_program["program_id"]

    year_resp = create_program_year(client, token=admin_token, program_id=program_id)
    assert year_resp.status_code in (200, 201), year_resp.text

    specialisation_resp = create_specialisation(client, token=admin_token, program_id=program_id)
    assert specialisation_resp.status_code in (200, 201), specialisation_resp.text

    return {
        "program_id": program_id,
        "program_year_id": year_resp.json()["program_year_id"],
        "specialisation_id": specialisation_resp.json()["specialisation_id"],
    }


def test_create_program_success(client, admin_token):
    response = create_program(client, token=admin_token)

    assert response.status_code in (200, 201)
    data = response.json()
    expected = program_data_factory()
    assert data["title_sv"] == expected["title_sv"]
    assert data["title_en"] == expected["title_en"]
    assert "program_id" in data


@pytest.mark.parametrize("token_fixture, expected_status", [("member_token", 403), (None, 401)])
def test_create_program_requires_permission(client, request, token_fixture, expected_status):
    token = request.getfixturevalue(token_fixture) if token_fixture else None

    response = create_program(client, token=token)
    assert response.status_code == expected_status


def test_program_read_endpoints_are_public(client, admin_token):
    create_response = create_program(client, token=admin_token)
    assert create_response.status_code in (200, 201)
    program_id = create_response.json()["program_id"]

    list_response = client.get("/programs/")
    assert list_response.status_code == 200
    assert any(program["program_id"] == program_id for program in list_response.json())

    detail_response = client.get(f"/programs/{program_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["program_id"] == program_id


def test_update_program_success(client, admin_token):
    create_response = create_program(client, token=admin_token)
    assert create_response.status_code in (200, 201)
    program_id = create_response.json()["program_id"]

    update_data = program_data_factory(title_sv="Uppdaterat program", title_en="Updated program")
    update_response = client.patch(
        f"/programs/{program_id}",
        json=update_data,
        headers=auth_headers(admin_token),
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title_sv"] == "Uppdaterat program"
    assert data["title_en"] == "Updated program"


def test_delete_program_success(client, admin_token):
    create_response = create_program(client, token=admin_token)
    assert create_response.status_code in (200, 201)
    program_id = create_response.json()["program_id"]

    get_response = client.get(f"/programs/{program_id}")
    assert get_response.status_code in (200, 201)

    delete_response = client.delete(f"/programs/{program_id}", headers=auth_headers(admin_token))
    assert delete_response.status_code == 200

    get_response = client.get(f"/programs/{program_id}")
    assert get_response.status_code == 404


def test_create_program_year_success(client, admin_token, base_program):
    program_id = base_program["program_id"]

    response = create_program_year(client, token=admin_token, program_id=program_id)
    assert response.status_code in (200, 201)

    data = response.json()
    expected = program_year_data_factory(program_id=program_id)
    assert data["program_id"] == program_id
    assert data["title_sv"] == expected["title_sv"]
    assert "program_year_id" in data


def test_create_program_year_requires_existing_program(client, admin_token):
    response = create_program_year(client, token=admin_token, program_id=999999)
    assert response.status_code == 400


def test_update_program_year_success(client, admin_token, base_program):
    program_id = base_program["program_id"]
    create_year_response = create_program_year(client, token=admin_token, program_id=program_id)
    assert create_year_response.status_code in (200, 201)
    program_year_id = create_year_response.json()["program_year_id"]

    update_data = program_year_data_factory(
        program_id=program_id,
        title_sv="Årskurs 2",
        title_en="Year 2",
    )
    response = client.patch(
        f"/program-years/{program_year_id}",
        json=update_data,
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title_sv"] == "Årskurs 2"
    assert data["title_en"] == "Year 2"


def test_delete_program_year_success(client, admin_token, base_program):
    program_id = base_program["program_id"]
    create_year_response = create_program_year(client, token=admin_token, program_id=program_id)
    assert create_year_response.status_code in (200, 201)
    program_year_id = create_year_response.json()["program_year_id"]

    get_response = client.get(f"/program-years/{program_year_id}")
    assert get_response.status_code in (200, 201)

    response = client.delete(f"/program-years/{program_year_id}", headers=auth_headers(admin_token))
    assert response.status_code == 200

    get_response = client.get(f"/program-years/{program_year_id}")
    assert get_response.status_code == 404


@pytest.mark.parametrize("token_fixture, expected_status", [("member_token", 403), (None, 401)])
def test_create_program_year_requires_permission(client, request, token_fixture, expected_status, base_program):
    token = request.getfixturevalue(token_fixture) if token_fixture else None

    response = create_program_year(client, token=token, program_id=base_program["program_id"])
    assert response.status_code == expected_status


def test_create_specialisation_success(client, admin_token, base_program):
    program_id = base_program["program_id"]

    response = create_specialisation(client, token=admin_token, program_id=program_id)
    assert response.status_code in (200, 201)

    data = response.json()
    expected = specialisation_data_factory(program_id=program_id)
    assert data["program_id"] == program_id
    assert data["title_sv"] == expected["title_sv"]
    assert "specialisation_id" in data


def test_create_specialisation_requires_existing_program(client, admin_token):
    response = create_specialisation(client, token=admin_token, program_id=999999)
    assert response.status_code == 400


def test_update_specialisation_success(client, admin_token, base_program):
    program_id = base_program["program_id"]
    create_specialisation_response = create_specialisation(client, token=admin_token, program_id=program_id)
    assert create_specialisation_response.status_code in (200, 201)
    specialisation_id = create_specialisation_response.json()["specialisation_id"]

    update_data = specialisation_data_factory(
        program_id=program_id,
        title_sv="Datateknik",
        title_en="Computer engineering",
    )
    response = client.patch(
        f"/specialisations/{specialisation_id}",
        json=update_data,
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title_sv"] == "Datateknik"
    assert data["title_en"] == "Computer engineering"


def test_delete_specialisation_success(client, admin_token, base_program):
    program_id = base_program["program_id"]
    create_specialisation_response = create_specialisation(client, token=admin_token, program_id=program_id)
    assert create_specialisation_response.status_code in (200, 201)
    specialisation_id = create_specialisation_response.json()["specialisation_id"]

    get_response = client.get(f"/specialisations/{specialisation_id}")
    assert get_response.status_code in (200, 201)

    response = client.delete(f"/specialisations/{specialisation_id}", headers=auth_headers(admin_token))
    assert response.status_code == 200

    get_response = client.get(f"/specialisations/{specialisation_id}")
    assert get_response.status_code == 404


@pytest.mark.parametrize("token_fixture, expected_status", [("member_token", 403), (None, 401)])
def test_create_specialisation_requires_permission(client, request, token_fixture, expected_status, base_program):
    token = request.getfixturevalue(token_fixture) if token_fixture else None

    response = create_specialisation(client, token=token, program_id=base_program["program_id"])
    assert response.status_code == expected_status


def test_create_course_with_relationships_success(client, admin_token, plugg_relationship_ids):
    payload = course_data_factory(
        title="Diskret matematik",
        course_code="FMAB10",
        description="Relations and graphs",
        program_year_ids=[plugg_relationship_ids["program_year_id"]],
        specialisation_ids=[plugg_relationship_ids["specialisation_id"]],
    )

    response = create_course(client, token=admin_token, **payload)
    assert response.status_code in (200, 201), response.text

    data = response.json()
    assert data["title"] == "Diskret matematik"
    assert data["course_code"] == "FMAB10"
    assert {year["program_year_id"] for year in data["program_years"]} == {plugg_relationship_ids["program_year_id"]}
    assert {spec["specialisation_id"] for spec in data["specialisations"]} == {
        plugg_relationship_ids["specialisation_id"]
    }


def test_create_course_with_missing_relationships_returns_404(client, admin_token):
    payload = course_data_factory(
        title="Ogiltig kurs",
        course_code="FMAB11",
        program_year_ids=[123456],
        specialisation_ids=[654321],
    )

    response = create_course(client, token=admin_token, **payload)
    assert response.status_code == 404


def test_update_course_relationships_success(client, admin_token, plugg_relationship_ids):
    program_id = plugg_relationship_ids["program_id"]

    year_resp = create_program_year(
        client,
        token=admin_token,
        **program_year_data_factory(program_id=program_id, title_sv="Arskurs 3", title_en="Year 3"),
    )
    assert year_resp.status_code in (200, 201), year_resp.text
    new_program_year_id = year_resp.json()["program_year_id"]

    specialisation_resp = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(program_id=program_id, title_sv="Datavetenskap", title_en="Computer science"),
    )
    assert specialisation_resp.status_code in (200, 201), specialisation_resp.text
    new_specialisation_id = specialisation_resp.json()["specialisation_id"]

    create_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Flervariabelanalys",
            course_code="FMAB12",
            program_year_ids=[plugg_relationship_ids["program_year_id"]],
            specialisation_ids=[plugg_relationship_ids["specialisation_id"]],
        ),
    )
    assert create_response.status_code in (200, 201), create_response.text
    course_id = create_response.json()["course_id"]

    update_payload = course_data_factory(
        title="Flervariabelanalys forts",
        course_code="FMAB12",
        description="Updated course",
        program_year_ids=[new_program_year_id],
        specialisation_ids=[new_specialisation_id],
    )
    update_response = client.patch(
        f"/courses/{course_id}",
        json=update_payload,
        headers=auth_headers(admin_token),
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["title"] == "Flervariabelanalys forts"
    assert {year["program_year_id"] for year in data["program_years"]} == {new_program_year_id}
    assert {spec["specialisation_id"] for spec in data["specialisations"]} == {new_specialisation_id}


def test_course_read_endpoints_are_public(client, admin_token, plugg_relationship_ids):
    create_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Signaler och system",
            course_code="ETIA20",
            program_year_ids=[plugg_relationship_ids["program_year_id"]],
            specialisation_ids=[plugg_relationship_ids["specialisation_id"]],
        ),
    )
    assert create_response.status_code in (200, 201), create_response.text
    course_id = create_response.json()["course_id"]

    list_response = client.get("/courses/")
    assert list_response.status_code == 200
    assert any(course["course_id"] == course_id for course in list_response.json())

    detail_response = client.get(f"/courses/{course_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["course_id"] == course_id


@pytest.mark.parametrize("token_fixture, expected_status", [("member_token", 403), (None, 401)])
def test_create_course_requires_permission(
    client,
    request,
    token_fixture,
    expected_status,
    plugg_relationship_ids,
):
    token = request.getfixturevalue(token_fixture) if token_fixture else None

    response = create_course(
        client,
        token=token,
        **course_data_factory(
            title="Operativsystem",
            course_code="EDA092",
            program_year_ids=[plugg_relationship_ids["program_year_id"]],
            specialisation_ids=[plugg_relationship_ids["specialisation_id"]],
        ),
    )
    assert response.status_code == expected_status


def test_delete_course_success(client, admin_token, plugg_relationship_ids):
    create_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Datastrukturer",
            course_code="EDA123",
            program_year_ids=[plugg_relationship_ids["program_year_id"]],
            specialisation_ids=[plugg_relationship_ids["specialisation_id"]],
        ),
    )
    assert create_response.status_code in (200, 201), create_response.text
    course_id = create_response.json()["course_id"]

    get_response = client.get(f"/courses/{course_id}")
    assert get_response.status_code in (200, 201)

    delete_response = client.delete(f"/courses/{course_id}", headers=auth_headers(admin_token))
    assert delete_response.status_code == 200

    get_response = client.get(f"/courses/{course_id}")
    assert get_response.status_code == 404
