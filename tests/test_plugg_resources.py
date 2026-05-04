# type: ignore
import os
import pytest

from .basic_factories import (
    auth_headers,
    create_associated_image,
    course_data_factory,
    create_course,
    create_course_document,
    create_program,
    create_program_year,
    create_specialisation,
    program_data_factory,
    program_year_data_factory,
    specialisation_data_factory,
)

from helpers.url_formatter import url_formatter


@pytest.fixture
def base_program(client, admin_token):
    response = create_program(client, token=admin_token)
    assert response.status_code in (200, 201), response.text
    return response.json()


@pytest.fixture
def plugg_relationship_ids(client, admin_token, base_program):
    # Create a program year and specialisation, then link them to the program, so we can test course creation with relationships in one go.
    program_id = base_program["program_id"]

    year_resp = create_program_year(client, token=admin_token, program_id=program_id)
    assert year_resp.status_code in (200, 201), year_resp.text

    specialisation_resp = create_specialisation(client, token=admin_token)
    assert specialisation_resp.status_code in (200, 201), specialisation_resp.text
    specialisation_id = specialisation_resp.json()["specialisation_id"]

    link_response = client.patch(
        f"/programs/{program_id}",
        json=program_data_factory(
            title_sv=base_program["title_sv"],
            title_en=base_program["title_en"],
            description_sv=base_program["description_sv"],
            description_en=base_program["description_en"],
            specialisation_ids=[specialisation_id],
        ),
        headers=auth_headers(admin_token),
    )
    assert link_response.status_code == 200, link_response.text

    return {
        "program_id": program_id,
        "program_year_id": year_resp.json()["program_year_id"],
        "specialisation_id": specialisation_id,
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


def test_program_get_by_url_title_success(client, admin_token):
    create_response = create_program(
        client,
        token=admin_token,
        **program_data_factory(title_sv="Datateknik", title_en="Computer engineering"),
    )
    assert create_response.status_code in (200, 201), create_response.text
    program_id = create_response.json()["program_id"]

    by_url_response = client.get("/programs/by_url_title/computer-engineering")
    assert by_url_response.status_code == 200, by_url_response.text
    assert by_url_response.json()["program_id"] == program_id


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


def test_program_cross_language_urlized_title_collision_returns_409(client, admin_token):
    first_response = create_program(
        client,
        token=admin_token,
        **program_data_factory(
            title_sv="Datateknik",
            title_en="Computer engineering",
        ),
    )
    assert first_response.status_code in (200, 201), first_response.text

    second_response = create_program(
        client,
        token=admin_token,
        **program_data_factory(
            title_sv="Computer engineering",
            title_en="Program B",
        ),
    )
    assert second_response.status_code == 409


def test_program_cross_language_collision_with_two_existing_programs_returns_409(client, admin_token):
    first_response = create_program(
        client,
        token=admin_token,
        **program_data_factory(
            title_sv="Datateknik",
            title_en="Program A",
        ),
    )
    assert first_response.status_code in (200, 201), first_response.text

    second_response = create_program(
        client,
        token=admin_token,
        **program_data_factory(
            title_sv="Reglersystem",
            title_en="Signal processing",
        ),
    )
    assert second_response.status_code in (200, 201), second_response.text

    colliding_response = create_program(
        client,
        token=admin_token,
        **program_data_factory(
            title_sv="Datateknik",
            title_en="Signal processing",
        ),
    )
    assert colliding_response.status_code == 409


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


def test_program_year_get_by_url_title_success(client, admin_token, base_program):
    program_id = base_program["program_id"]
    create_response = create_program_year(
        client,
        token=admin_token,
        **program_year_data_factory(
            program_id=program_id,
            title_sv="Årskurs 1",
            title_en="Year one",
        ),
    )
    assert create_response.status_code in (200, 201), create_response.text
    program_year_id = create_response.json()["program_year_id"]

    by_url_response = client.get(f"/program-years/by_url_title/{url_formatter(base_program['title_sv'])}/arskurs-1")
    assert by_url_response.status_code == 200, by_url_response.text
    assert by_url_response.json()["program_year_id"] == program_year_id


def test_program_year_duplicate_urlized_title_same_program_returns_409(client, admin_token, base_program):
    program_id = base_program["program_id"]
    first_response = create_program_year(
        client,
        token=admin_token,
        **program_year_data_factory(program_id=program_id, title_sv="Årskurs 2", title_en="Year two"),
    )
    assert first_response.status_code in (200, 201), first_response.text

    second_response = create_program_year(
        client,
        token=admin_token,
        **program_year_data_factory(program_id=program_id, title_sv="Arskurs 2!!!", title_en="Year två"),
    )
    assert second_response.status_code == 409


def test_program_year_cross_language_urlized_title_collision_same_program_returns_409(
    client, admin_token, base_program
):
    program_id = base_program["program_id"]
    first_response = create_program_year(
        client,
        token=admin_token,
        **program_year_data_factory(
            program_id=program_id,
            title_sv="Årskurs 5",
            title_en="Year five",
        ),
    )
    assert first_response.status_code in (200, 201), first_response.text

    second_response = create_program_year(
        client,
        token=admin_token,
        **program_year_data_factory(
            program_id=program_id,
            title_sv="Year five",
            title_en="Årskurs 6",
        ),
    )
    assert second_response.status_code == 409


def test_program_year_duplicate_urlized_title_different_program_allowed(client, admin_token, base_program):
    first_program_id = base_program["program_id"]
    second_program_response = create_program(
        client,
        token=admin_token,
        **program_data_factory(title_sv="Väg och vatten", title_en="Civil engineering"),
    )
    assert second_program_response.status_code in (200, 201), second_program_response.text
    second_program_id = second_program_response.json()["program_id"]

    first_response = create_program_year(
        client,
        token=admin_token,
        **program_year_data_factory(program_id=first_program_id, title_sv="Årskurs 3", title_en="Year three"),
    )
    assert first_response.status_code in (200, 201), first_response.text

    second_response = create_program_year(
        client,
        token=admin_token,
        **program_year_data_factory(program_id=second_program_id, title_sv="Arskurs 3", title_en="Year three"),
    )
    assert second_response.status_code in (200, 201), second_response.text

    second_program_year_id = second_response.json()["program_year_id"]
    by_url_response = client.get(
        f"/program-years/by_url_title/{url_formatter(second_program_response.json()['title_sv'])}/arskurs-3"
    )
    assert by_url_response.status_code == 200, by_url_response.text
    assert by_url_response.json()["program_year_id"] == second_program_year_id


def test_create_specialisation_success(client, admin_token):
    response = create_specialisation(client, token=admin_token)
    assert response.status_code in (200, 201)

    data = response.json()
    expected = specialisation_data_factory()
    assert data["programs"] == []
    assert data["title_sv"] == expected["title_sv"]
    assert "specialisation_id" in data


def test_specialisation_get_by_url_title_success(client, admin_token):
    create_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(title_sv="Signalbehandling", title_en="Signal processing"),
    )
    assert create_response.status_code in (200, 201), create_response.text
    specialisation_id = create_response.json()["specialisation_id"]

    by_url_response = client.get("/specialisations/by_url_title/signal-processing")
    assert by_url_response.status_code == 200, by_url_response.text
    assert by_url_response.json()["specialisation_id"] == specialisation_id


def test_specialisation_cross_language_urlized_title_collision_returns_409(client, admin_token):
    first_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(
            title_sv="Reglersystem",
            title_en="Control systems",
        ),
    )
    assert first_response.status_code in (200, 201), first_response.text

    second_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(
            title_sv="Control systems",
            title_en="Specialisering B",
        ),
    )
    assert second_response.status_code == 409


def test_create_program_requires_existing_specialisation(client, admin_token):
    response = create_program(client, token=admin_token, specialisation_ids=[999999])
    assert response.status_code == 404


def test_update_specialisation_success(client, admin_token):
    create_specialisation_response = create_specialisation(client, token=admin_token)
    assert create_specialisation_response.status_code in (200, 201)
    specialisation_id = create_specialisation_response.json()["specialisation_id"]

    update_data = specialisation_data_factory(
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


def test_delete_specialisation_success(client, admin_token):
    create_specialisation_response = create_specialisation(client, token=admin_token)
    assert create_specialisation_response.status_code in (200, 201)
    specialisation_id = create_specialisation_response.json()["specialisation_id"]

    get_response = client.get(f"/specialisations/{specialisation_id}")
    assert get_response.status_code in (200, 201)

    response = client.delete(f"/specialisations/{specialisation_id}", headers=auth_headers(admin_token))
    assert response.status_code == 200

    get_response = client.get(f"/specialisations/{specialisation_id}")
    assert get_response.status_code == 404


def test_create_program_with_multiple_specialisations_success(client, admin_token):
    first_specialisation_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(title_sv="Inbyggda system", title_en="Embedded systems"),
    )
    assert first_specialisation_response.status_code in (200, 201), first_specialisation_response.text
    first_specialisation_id = first_specialisation_response.json()["specialisation_id"]

    second_specialisation_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(title_sv="Reglersystem", title_en="Control systems"),
    )
    assert second_specialisation_response.status_code in (200, 201), second_specialisation_response.text
    second_specialisation_id = second_specialisation_response.json()["specialisation_id"]

    response = create_program(
        client,
        token=admin_token,
        **program_data_factory(
            title_sv="Teknisk fysik",
            title_en="Engineering physics",
            specialisation_ids=[first_specialisation_id, second_specialisation_id],
        ),
    )

    assert response.status_code in (200, 201), response.text
    data = response.json()
    assert data["title_sv"] == "Teknisk fysik"
    assert {specialisation["specialisation_id"] for specialisation in data["specialisations"]} == {
        first_specialisation_id,
        second_specialisation_id,
    }


def test_update_program_specialisation_associations_success(client, admin_token):
    first_specialisation_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(title_sv="AI och data", title_en="AI and data"),
    )
    assert first_specialisation_response.status_code in (200, 201), first_specialisation_response.text
    first_specialisation_id = first_specialisation_response.json()["specialisation_id"]

    second_specialisation_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(title_sv="Signalbehandling", title_en="Signal processing"),
    )
    assert second_specialisation_response.status_code in (200, 201), second_specialisation_response.text
    second_specialisation_id = second_specialisation_response.json()["specialisation_id"]

    third_specialisation_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(title_sv="Nätverk", title_en="Networks"),
    )
    assert third_specialisation_response.status_code in (200, 201), third_specialisation_response.text
    third_specialisation_id = third_specialisation_response.json()["specialisation_id"]

    create_response = create_program(
        client,
        token=admin_token,
        **program_data_factory(
            title_sv="Datateknik",
            title_en="Computer engineering",
            specialisation_ids=[first_specialisation_id, second_specialisation_id],
        ),
    )
    assert create_response.status_code in (200, 201), create_response.text
    program_id = create_response.json()["program_id"]

    update_response = client.patch(
        f"/programs/{program_id}",
        json={
            "title_sv": "Datateknik uppdaterad",
            "title_en": "Computer engineering updated",
            "specialisation_ids": [second_specialisation_id, third_specialisation_id],
            "description_sv": "Updated association",
            "description_en": "Updated association",
        },
        headers=auth_headers(admin_token),
    )

    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated["title_en"] == "Computer engineering updated"
    assert {specialisation["specialisation_id"] for specialisation in updated["specialisations"]} == {
        second_specialisation_id,
        third_specialisation_id,
    }


def test_program_reads_include_specialisation_associations(
    client,
    admin_token,
    db_session,
):
    first_specialisation_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(title_sv="Data science", title_en="Data science"),
    )
    assert first_specialisation_response.status_code in (200, 201), first_specialisation_response.text
    first_specialisation_id = first_specialisation_response.json()["specialisation_id"]

    second_specialisation_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(title_sv="AI", title_en="AI"),
    )
    assert second_specialisation_response.status_code in (200, 201), second_specialisation_response.text
    second_specialisation_id = second_specialisation_response.json()["specialisation_id"]

    program_response = create_program(
        client,
        token=admin_token,
        **program_data_factory(
            title_sv="Industriell ekonomi",
            title_en="Industrial engineering",
            specialisation_ids=[first_specialisation_id, second_specialisation_id],
        ),
    )
    assert program_response.status_code in (200, 201), program_response.text
    program_id = program_response.json()["program_id"]

    first_specialisation_detail = client.get(f"/specialisations/{first_specialisation_id}")
    assert first_specialisation_detail.status_code == 200, first_specialisation_detail.text

    second_specialisation_detail = client.get(f"/specialisations/{second_specialisation_id}")
    assert second_specialisation_detail.status_code == 200, second_specialisation_detail.text

    db_session.expire_all()

    program_detail = client.get(f"/programs/{program_id}")
    assert program_detail.status_code == 200, program_detail.text
    assert {specialisation["specialisation_id"] for specialisation in program_detail.json()["specialisations"]} == {
        first_specialisation_id,
        second_specialisation_id,
    }


def test_create_program_rolls_back_when_any_specialisation_id_is_missing(client, admin_token):
    first_specialisation_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(title_sv="Kemiteknik", title_en="Chemical engineering"),
    )
    assert first_specialisation_response.status_code in (200, 201), first_specialisation_response.text
    first_specialisation_id = first_specialisation_response.json()["specialisation_id"]

    second_specialisation_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(title_sv="Bioteknik", title_en="Biotechnology"),
    )
    assert second_specialisation_response.status_code in (200, 201), second_specialisation_response.text
    second_specialisation_id = second_specialisation_response.json()["specialisation_id"]

    payload = program_data_factory(
        title_sv="Rollback program",
        title_en="Rollback program",
        specialisation_ids=[first_specialisation_id, second_specialisation_id, 999999],
        description_sv="Should not persist",
        description_en="Should not persist",
    )

    before_list = client.get("/programs/")
    assert before_list.status_code == 200, before_list.text
    before_programs = before_list.json()
    before_count = len(before_programs)

    create_response = create_program(client, token=admin_token, **payload)
    assert create_response.status_code == 404

    after_list = client.get("/programs/")
    assert after_list.status_code == 200, after_list.text
    after_programs = after_list.json()

    assert len(after_programs) == before_count
    assert all(program["title_en"] != payload["title_en"] for program in after_programs)


def test_update_program_rolls_back_when_any_specialisation_id_is_missing(client, admin_token):
    first_specialisation_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(title_sv="Signalbehandling", title_en="Signal processing"),
    )
    assert first_specialisation_response.status_code in (200, 201), first_specialisation_response.text
    first_specialisation_id = first_specialisation_response.json()["specialisation_id"]

    second_specialisation_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(
            title_sv="Reglersystem",
            title_en="Control systems",
        ),
    )
    assert second_specialisation_response.status_code in (200, 201), second_specialisation_response.text
    second_specialisation_id = second_specialisation_response.json()["specialisation_id"]

    create_response = create_program(
        client,
        token=admin_token,
        **program_data_factory(
            title_sv="Farkostteknik",
            title_en="Vehicle engineering",
            specialisation_ids=[first_specialisation_id, second_specialisation_id],
        ),
    )
    assert create_response.status_code in (200, 201), create_response.text
    created_program = create_response.json()
    program_id = created_program["program_id"]

    update_payload = program_data_factory(
        title_sv="Farkostteknik uppdaterad",
        title_en="Vehicle engineering updated",
        specialisation_ids=[second_specialisation_id, 999999],
        description_sv="Should not persist update",
        description_en="Should not persist update",
    )
    update_response = client.patch(
        f"/programs/{program_id}",
        json=update_payload,
        headers=auth_headers(admin_token),
    )
    assert update_response.status_code == 404

    detail_response = client.get(f"/programs/{program_id}")
    assert detail_response.status_code == 200, detail_response.text
    detail_data = detail_response.json()

    assert detail_data["title_en"] == created_program["title_en"]
    assert {specialisation["specialisation_id"] for specialisation in detail_data["specialisations"]} == {
        first_specialisation_id,
        second_specialisation_id,
    }


@pytest.mark.parametrize("token_fixture, expected_status", [("member_token", 403), (None, 401)])
def test_create_specialisation_requires_permission(client, request, token_fixture, expected_status):
    token = request.getfixturevalue(token_fixture) if token_fixture else None

    response = create_specialisation(client, token=token)
    assert response.status_code == expected_status


def test_create_course_success(client, admin_token):
    payload = course_data_factory(
        title="Diskret matematik",
        course_code="FMAB10",
        description="Relations and graphs",
    )

    response = create_course(client, token=admin_token, **payload)
    assert response.status_code in (200, 201), response.text

    data = response.json()
    assert data["title"] == "Diskret matematik"
    assert data["course_code"] == "FMAB10"
    assert data["program_years"] == []
    assert data["specialisations"] == []


def test_course_get_by_url_title_success(client, admin_token):
    create_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(title="Reglerteori"),
    )
    assert create_response.status_code in (200, 201), create_response.text
    course_id = create_response.json()["course_id"]

    by_url_response = client.get("/courses/by_url_title/reglerteori")
    assert by_url_response.status_code == 200, by_url_response.text
    assert by_url_response.json()["course_id"] == course_id


def test_create_course_with_duplicate_urlized_title_returns_409(client, admin_token):
    first_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Reglerteori",
            course_code="FRTN05",
        ),
    )
    assert first_response.status_code in (200, 201), first_response.text

    second_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Reglerteöri!!!",
            course_code="FRTN06",
        ),
    )
    assert second_response.status_code == 409


def test_create_course_with_duplicate_course_code_fails(client, admin_token):
    first_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Reglerteori grund",
            course_code="FRTN07",
        ),
    )
    assert first_response.status_code in (200, 201), first_response.text

    second_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Reglerteori forts",
            course_code="FRTN07",
        ),
    )
    assert second_response.status_code in (400, 409)


def test_update_course_with_duplicate_urlized_title_returns_409(client, admin_token):
    first_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Mekanik",
            course_code="FMEA10",
        ),
    )
    assert first_response.status_code in (200, 201), first_response.text

    second_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Termodynamik",
            course_code="FMEA11",
        ),
    )
    assert second_response.status_code in (200, 201), second_response.text

    second_course_id = second_response.json()["course_id"]
    update_response = client.patch(
        f"/courses/{second_course_id}",
        json=course_data_factory(
            title="  mekaNIK  ",
            course_code="FMEA11",
        ),
        headers=auth_headers(admin_token),
    )
    assert update_response.status_code == 409


def test_create_program_year_requires_existing_course(client, admin_token, base_program):
    response = create_program_year(
        client,
        token=admin_token,
        **program_year_data_factory(program_id=base_program["program_id"], course_ids=[999999]),
    )
    assert response.status_code == 404


def test_create_program_year_with_course_relationships_success(
    client,
    admin_token,
    base_program,
):
    course_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(title="Rollteori", course_code="FMAB11"),
    )
    assert course_response.status_code in (200, 201), course_response.text
    course_id = course_response.json()["course_id"]

    program_year_response = create_program_year(
        client,
        token=admin_token,
        **program_year_data_factory(program_id=base_program["program_id"], course_ids=[course_id]),
    )
    assert program_year_response.status_code in (200, 201), program_year_response.text

    data = program_year_response.json()
    assert data["program_id"] == base_program["program_id"]
    assert {course["course_id"] for course in data["courses"]} == {course_id}


def test_create_program_year_rolls_back_when_any_course_id_is_missing(client, admin_token, base_program):
    course_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(title="Rollback course", course_code="RBKPY001"),
    )
    assert course_response.status_code in (200, 201), course_response.text
    course_id = course_response.json()["course_id"]

    payload = program_year_data_factory(
        program_id=base_program["program_id"],
        title_sv="Rollback årskurs",
        title_en="Rollback year",
        course_ids=[course_id, 999999],
    )

    before_list = client.get("/program-years/")
    assert before_list.status_code == 200, before_list.text
    before_count = len(before_list.json())

    response = create_program_year(client, token=admin_token, **payload)
    assert response.status_code == 404

    after_list = client.get("/program-years/")
    assert after_list.status_code == 200, after_list.text
    after_program_years = after_list.json()

    assert len(after_program_years) == before_count
    assert all(program_year["title_en"] != payload["title_en"] for program_year in after_program_years)


def test_update_program_year_course_associations_success(client, admin_token, base_program):
    first_course_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(title="Flervariabelanalys", course_code="FMAB12"),
    )
    assert first_course_response.status_code in (200, 201), first_course_response.text
    first_course_id = first_course_response.json()["course_id"]

    second_course_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(title="Flervariabelanalys forts", course_code="FMAB13"),
    )
    assert second_course_response.status_code in (200, 201), second_course_response.text
    second_course_id = second_course_response.json()["course_id"]

    create_program_year_response = create_program_year(
        client,
        token=admin_token,
        **program_year_data_factory(
            program_id=base_program["program_id"],
            title_sv="Årskurs 4",
            title_en="Year 4",
            course_ids=[first_course_id],
        ),
    )
    assert create_program_year_response.status_code in (200, 201), create_program_year_response.text
    program_year_id = create_program_year_response.json()["program_year_id"]

    update_response = client.patch(
        f"/program-years/{program_year_id}",
        json=program_year_data_factory(
            program_id=base_program["program_id"],
            title_sv="Årskurs 4 uppdaterad",
            title_en="Year 4 updated",
            course_ids=[second_course_id],
        ),
        headers=auth_headers(admin_token),
    )
    assert update_response.status_code == 200, update_response.text

    updated = update_response.json()
    assert updated["title_en"] == "Year 4 updated"
    assert {course["course_id"] for course in updated["courses"]} == {second_course_id}


def test_create_specialisation_with_course_relationships_success(client, admin_token):
    course_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Sannolikhetsteori",
            course_code="FMSF70",
        ),
    )
    assert course_response.status_code in (200, 201), course_response.text
    course_id = course_response.json()["course_id"]

    specialisation_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(
            title_sv="Sannolikhet och statistik",
            title_en="Probability and statistics",
            course_ids=[course_id],
        ),
    )
    assert specialisation_response.status_code in (200, 201), specialisation_response.text
    data = specialisation_response.json()
    assert {course["course_id"] for course in data["courses"]} == {course_id}


def test_create_specialisation_requires_existing_course(client, admin_token):
    response = create_specialisation(client, token=admin_token, course_ids=[999999])
    assert response.status_code == 404


def test_update_specialisation_course_associations_success(client, admin_token):
    first_course_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Kommunikation",
            course_code="EITA15",
        ),
    )
    assert first_course_response.status_code in (200, 201), first_course_response.text
    first_course_id = first_course_response.json()["course_id"]

    second_course_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Reglerteknik",
            course_code="FRTN01",
        ),
    )
    assert second_course_response.status_code in (200, 201), second_course_response.text
    second_course_id = second_course_response.json()["course_id"]

    create_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(
            title_sv="AI och data",
            title_en="AI and data",
            course_ids=[first_course_id],
        ),
    )
    assert create_response.status_code in (200, 201), create_response.text
    specialisation_id = create_response.json()["specialisation_id"]

    update_response = client.patch(
        f"/specialisations/{specialisation_id}",
        json={
            "title_sv": "AI och data uppdaterad",
            "title_en": "AI and data updated",
            "course_ids": [second_course_id],
            "description_sv": "Updated association",
            "description_en": "Updated association",
        },
        headers=auth_headers(admin_token),
    )

    assert update_response.status_code == 200, update_response.text
    updated = update_response.json()
    assert updated["title_en"] == "AI and data updated"
    assert {course["course_id"] for course in updated["courses"]} == {second_course_id}


def test_create_specialisation_rolls_back_when_any_course_id_is_missing(client, admin_token):
    course_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Signaler",
            course_code="EITA20",
        ),
    )
    assert course_response.status_code in (200, 201), course_response.text
    valid_course_id = course_response.json()["course_id"]

    payload = specialisation_data_factory(
        title_sv="Rollback specialisering",
        title_en="Rollback specialisation",
        course_ids=[valid_course_id, 999999],
    )

    before_list = client.get("/specialisations/")
    assert before_list.status_code == 200, before_list.text
    before_count = len(before_list.json())

    create_response = create_specialisation(client, token=admin_token, **payload)
    assert create_response.status_code == 404

    after_list = client.get("/specialisations/")
    assert after_list.status_code == 200, after_list.text
    after_specialisations = after_list.json()

    assert len(after_specialisations) == before_count
    assert all(specialisation["title_en"] != payload["title_en"] for specialisation in after_specialisations)


def test_update_specialisation_rolls_back_when_any_course_id_is_missing(client, admin_token):
    first_course_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Nätverk",
            course_code="EITF65",
        ),
    )
    assert first_course_response.status_code in (200, 201), first_course_response.text
    first_course_id = first_course_response.json()["course_id"]

    second_course_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Distribuerade system",
            course_code="EDA040",
        ),
    )
    assert second_course_response.status_code in (200, 201), second_course_response.text
    second_course_id = second_course_response.json()["course_id"]

    create_response = create_specialisation(
        client,
        token=admin_token,
        **specialisation_data_factory(
            title_sv="Signalbehandling",
            title_en="Signal processing",
            course_ids=[first_course_id],
        ),
    )
    assert create_response.status_code in (200, 201), create_response.text
    created_specialisation = create_response.json()
    specialisation_id = created_specialisation["specialisation_id"]

    update_payload = specialisation_data_factory(
        title_sv="Signalbehandling uppdaterad",
        title_en="Signal processing updated",
        course_ids=[second_course_id, 999999],
        description_sv="Should not persist update",
        description_en="Should not persist update",
    )
    update_response = client.patch(
        f"/specialisations/{specialisation_id}",
        json=update_payload,
        headers=auth_headers(admin_token),
    )
    assert update_response.status_code == 404

    detail_response = client.get(f"/specialisations/{specialisation_id}")
    assert detail_response.status_code == 200, detail_response.text
    detail_data = detail_response.json()

    assert detail_data["title_en"] == created_specialisation["title_en"]
    assert {course["course_id"] for course in detail_data["courses"]} == {first_course_id}


def test_course_read_endpoints_are_public(client, admin_token):
    create_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Signaler och system",
            course_code="ETIA20",
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
):
    token = request.getfixturevalue(token_fixture) if token_fixture else None

    response = create_course(
        client,
        token=token,
        **course_data_factory(
            title="Operativsystem",
            course_code="EDA092",
        ),
    )
    assert response.status_code == expected_status


def test_delete_course_success(client, admin_token):
    create_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Datastrukturer",
            course_code="EDA123",
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


def test_delete_course_removes_associated_images_and_course_documents_from_db_and_filesystem(
    client,
    admin_token,
    db_session,
    example_file,
    example_image_file,
):
    from db_models.associated_img_model import AssociatedImg_DB
    from db_models.course_document_model import CourseDocument_DB

    create_response = create_course(
        client,
        token=admin_token,
        **course_data_factory(
            title="Databasteknik",
            course_code="EDA216",
        ),
    )
    assert create_response.status_code in (200, 201), create_response.text
    course_id = create_response.json()["course_id"]

    upload_image_response = create_associated_image(
        client,
        token=admin_token,
        association_type="course",
        association_id=course_id,
        file=example_image_file,
    )
    assert upload_image_response.status_code in (200, 201), upload_image_response.text

    course_response = client.get(f"/courses/{course_id}")
    assert course_response.status_code == 200, course_response.text
    associated_img_id = course_response.json()["associated_img_id"]
    assert associated_img_id is not None

    associated_img = db_session.query(AssociatedImg_DB).filter_by(associated_img_id=associated_img_id).one_or_none()
    assert associated_img is not None
    associated_img_path = associated_img.path
    assert os.path.exists(associated_img_path)

    create_document_response = create_course_document(
        client,
        token=admin_token,
        file=example_file,
        course_id=course_id,
        title="Föreläsningsanteckningar",
        author="Ingen",
        category="Notes",
        sub_category="VT26",
    )
    assert create_document_response.status_code in (200, 201), create_document_response.text
    course_document_id = create_document_response.json()["course_document_id"]

    course_document = db_session.query(CourseDocument_DB).filter_by(course_document_id=course_document_id).one_or_none()
    assert course_document is not None

    document_base_path = os.environ["COURSE_DOCUMENT_BASE_PATH"]
    course_document_path = os.path.join(document_base_path, course_document.file_name)
    assert os.path.exists(course_document_path)

    delete_response = client.delete(f"/courses/{course_id}", headers=auth_headers(admin_token))
    assert delete_response.status_code == 200, delete_response.text

    deleted_associated_img = (
        db_session.query(AssociatedImg_DB).filter_by(associated_img_id=associated_img_id).one_or_none()
    )
    deleted_course_document = (
        db_session.query(CourseDocument_DB).filter_by(course_document_id=course_document_id).one_or_none()
    )

    assert deleted_associated_img is None
    assert deleted_course_document is None
    assert not os.path.exists(associated_img_path)
    assert not os.path.exists(course_document_path)
