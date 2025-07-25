# type: ignore
from fastapi import status
from .basic_factories import auth_headers


def test_admin_update_user_posts(client, membered_user, admin_post, admin_token):
    """Admin can assign a post to a user."""
    # Initially user has no posts
    response = client.get(f"/users/{membered_user.id}", headers=auth_headers(admin_token))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "posts" in data
    assert len(data["posts"]) == 0

    # Now assign a post to the user
    response = client.patch(
        f"/users/admin/user-posts/{membered_user.id}",
        json={"post_ids": [admin_post.id]},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # posts list should now contain our admin_post
    assert any(p["id"] == admin_post.id for p in data["posts"])


def test_admin_remove_user_posts(client, membered_user, admin_post, admin_token):
    """Admin can remove posts not in the provided list."""
    # First add the post
    client.patch(
        f"/users/admin/user-posts/{membered_user.id}",
        json={"post_ids": [admin_post.id]},
        headers=auth_headers(admin_token),
    )
    # Now remove it by sending empty list -> all posts should be removed
    response = client.patch(
        f"/users/admin/user-posts/{membered_user.id}",
        json={"post_ids": []},
        headers=auth_headers(admin_token),
    )
    data = response.json()
    assert data["posts"] == []  # All posts should be removed


def test_admin_update_user_posts_invalid_post(client, membered_user, admin_token):
    """Updating with a non-existent post ID returns 404."""
    response = client.patch(
        f"/users/admin/user-posts/{membered_user.id}",
        json={"post_ids": [9999]},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_member_cannot_update_user_posts(member_token, client, admin_user, member_post):
    """Non-admin cannot update another user's posts."""
    response = client.patch(
        f"/users/admin/user-posts/{admin_user.id}",
        json={"post_ids": [member_post.id]},
        headers=auth_headers(member_token),
    )
    assert response.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED)


def test_add_and_remove_posts(client, membered_user, admin_post, admin_token, member_council_id):
    """Test adding and removing posts at the same time."""
    # Because we have called member_council_id fixture, the membered_user has a post in that council.
    # Now we will add the admin_post and remove the membered_user's post.
    response = client.patch(
        f"/users/admin/user-posts/{membered_user.id}",
        json={"post_ids": [admin_post.id]},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # The membered_user should now have the admin_post and not the member_council_id post
    assert any(p["id"] == admin_post.id for p in data["posts"])
    assert not any(p["council_id"] == member_council_id for p in data["posts"])
