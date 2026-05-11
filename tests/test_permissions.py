# type: ignore
import pytest
import ast
from pathlib import Path
from fastapi import status
from .basic_factories import auth_headers


# Bot written function to make sure that when we run tests using permissions below,
# the actual required permissions in the code are what we expect, to guard against silent permission drift.
# If this gives you trouble for whatever reason, just comment it out along with
# the parts of tests containing 'required_permission' found in the tests
def _extract_required_permission(router_file: Path, function_name: str):
    """Return (action, target) from Permission.require(action, target) in route dependencies."""

    module = ast.parse(router_file.read_text(encoding="utf-8"))

    for node in module.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != function_name:
            continue

        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue

            for keyword in decorator.keywords:
                if keyword.arg != "dependencies" or not isinstance(keyword.value, ast.List):
                    continue

                for dependency in keyword.value.elts:
                    if not isinstance(dependency, ast.Call):
                        continue
                    if not isinstance(dependency.func, ast.Attribute):
                        continue
                    if dependency.func.attr != "require":
                        continue
                    if not isinstance(dependency.func.value, ast.Name):
                        continue
                    if dependency.func.value.id != "Permission":
                        continue
                    if len(dependency.args) != 2:
                        continue
                    if not all(isinstance(arg, ast.Constant) and isinstance(arg.value, str) for arg in dependency.args):
                        continue

                    return dependency.args[0].value, dependency.args[1].value

        return None

    raise AssertionError(f"Function {function_name} not found in {router_file}")


def test_get_my_permissions(client, admin_token):
    """Test that the /permissions/me route returns some correct permissions for the admin user"""

    # Check that the admin user has some of the expected permissions
    response = client.get("/permissions/me", headers=auth_headers(admin_token))
    assert response.status_code == status.HTTP_200_OK
    permissions = response.json()
    assert ["manage", "User"] in permissions
    assert ["manage", "Permission"] in permissions
    assert ["manage", "BlahBlah"] not in permissions


def test_deny_super_for_manage(client, manage_user_post, membered_user, db_session, admin_user):
    """Test that a user with only manage permissions cannot access super permissions (like deleting a user)"""

    # Give appropriate permissions
    membered_user.posts.append(manage_user_post)
    db_session.commit()

    # Get token for the user with manage permissions
    resp = client.post("/auth/login", data={"username": "member@example.com", "password": "Password123"})
    user_token = resp.json()["access_token"]

    # Check that the admin delete user route requires super permissions, not just manage permissions
    # if this test fails due to permission drift, point it at some other route that requires super permissions
    router_file = Path(__file__).resolve().parents[1] / "routes" / "user_router.py"
    required_permission = _extract_required_permission(router_file, "admin_delete_user")
    assert required_permission == ("super", "User")

    # Check that the user has manage permissions but not super permissions
    response = client.get("/permissions/me", headers=auth_headers(user_token))
    assert response.status_code == status.HTTP_200_OK
    permissions = response.json()
    assert ["manage", "User"] in permissions
    assert ["super", "User"] not in permissions

    # Try to delete another user (which requires super permissions)
    response = client.delete(
        "/users/admin/" + str(admin_user.id),
        headers=auth_headers(user_token),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_allow_manage_for_super(client, super_user_post, membered_user, db_session, admin_user):
    """Test that a user with super permissions can access manage routes"""

    # Give appropriate permissions
    membered_user.posts.append(super_user_post)
    db_session.commit()

    # Get token for the user with super permissions
    resp = client.post("/auth/login", data={"username": "member@example.com", "password": "Password123"})
    user_token = resp.json()["access_token"]

    # Check that the admin manage user route requires manage permissions
    # if this test fails due to permission drift, point it at some other route that requires manage permissions
    router_file = Path(__file__).resolve().parents[1] / "routes" / "user_router.py"
    required_permission = _extract_required_permission(router_file, "admin_update_user")
    assert required_permission == ("manage", "User")

    # Check that the user has super permissions but not manage permissions
    response = client.get("/permissions/me", headers=auth_headers(user_token))
    assert response.status_code == status.HTTP_200_OK
    permissions = response.json()
    assert ["super", "User"] in permissions
    assert ["manage", "User"] not in permissions

    # The user should still be able to access the manage route
    response = client.patch(
        f"/users/admin/update/{str(admin_user.id)}",
        json={"first_name": "NewName"},
        headers=auth_headers(user_token),
    )
    assert response.status_code == status.HTTP_200_OK


def test_allow_view_for_manage(client, manage_user_post, membered_user, db_session, admin_user):
    """Test that a user with manage permissions can access view routes"""

    # Give appropriate permissions
    membered_user.posts.append(manage_user_post)
    db_session.commit()

    # Get token for the user with manage permissions
    resp = client.post("/auth/login", data={"username": "member@example.com", "password": "Password123"})
    user_token = resp.json()["access_token"]

    # Check that the view user route requires view permissions but not manage permissions
    # if this test fails due to permission drift, point it at some other route that requires view permissions
    router_file = Path(__file__).resolve().parents[1] / "routes" / "user_router.py"
    required_permission = _extract_required_permission(router_file, "get_user")
    assert required_permission == ("view", "User")

    # Check that the user has manage permissions but not view permissions
    response = client.get("/permissions/me", headers=auth_headers(user_token))
    assert response.status_code == status.HTTP_200_OK
    permissions = response.json()
    assert ["manage", "User"] in permissions
    assert ["view", "User"] not in permissions

    # The user should still be able to access the view route
    response = client.get(
        "/users/admin/" + str(admin_user.id),
        headers=auth_headers(user_token),
    )
    assert response.status_code == status.HTTP_200_OK


def test_deny_manage_for_view(client, view_user_post, membered_user, db_session, admin_user):
    """Test that a user with only view permissions cannot access manage routes"""

    # Give appropriate permissions
    membered_user.posts.append(view_user_post)
    db_session.commit()

    # Get token for the user with view permissions
    resp = client.post("/auth/login", data={"username": "member@example.com", "password": "Password123"})
    user_token = resp.json()["access_token"]

    # Check that the admin manage user route requires manage permissions, not just view permissions
    router_file = Path(__file__).resolve().parents[1] / "routes" / "user_router.py"
    required_permission = _extract_required_permission(router_file, "admin_update_user")
    assert required_permission == ("manage", "User")

    # Check that the user has view permissions but not manage permissions
    response = client.get("/permissions/me", headers=auth_headers(user_token))
    assert response.status_code == status.HTTP_200_OK
    permissions = response.json()
    assert ["view", "User"] in permissions
    assert ["manage", "User"] not in permissions

    # Try to access the manage route
    response = client.patch(
        f"/users/admin/update/{str(admin_user.id)}",
        json={"first_name": "NewName"},
        headers=auth_headers(user_token),
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_member_without_permissions_is_forbidden(client, member_token):
    """Test that a plain member without post permissions cannot access protected permission routes."""

    response = client.get("/permissions/", headers=auth_headers(member_token))
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_my_permissions_requires_member_status(client, non_member_token):
    """Test that /permissions/me returns null for verified non-members and anonymous users."""

    response = client.get("/permissions/me", headers=auth_headers(non_member_token))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is None

    response = client.get("/permissions/me")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is None
