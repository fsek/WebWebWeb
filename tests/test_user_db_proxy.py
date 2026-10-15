# type: ignore
import ast
import asyncio
import inspect
from fastapi_users.db import SQLAlchemyUserDatabase

from db_models.user_model import User_DB
from user.user_stuff import _AsyncSessionProxy

# We run fastapi-users' async-only SQLAlchemyUserDatabase on top of our sync Session via
# _AsyncSessionProxy, which only implements the session members that adapter happens to use.
# These tests pin that assumption down, so a fastapi-users-db-sqlalchemy bump that reaches for
# a new session member fails here instead of at request time in production.


def _session_members_used_by_adapter() -> set[str]:
    """Return every `self.session.<name>` attribute accessed in SQLAlchemyUserDatabase."""

    source = inspect.getsource(SQLAlchemyUserDatabase)
    tree = ast.parse(ast.unparse(ast.parse(source)))

    members: set[str] = set()
    for node in ast.walk(tree):
        # Match the attribute access `self.session.<name>`
        if not isinstance(node, ast.Attribute):
            continue
        inner = node.value
        if not isinstance(inner, ast.Attribute) or inner.attr != "session":
            continue
        if not isinstance(inner.value, ast.Name) or inner.value.id != "self":
            continue
        members.add(node.attr)

    assert members, "Found no `self.session.*` usage in SQLAlchemyUserDatabase - did the adapter change shape?"
    return members


def test_proxy_implements_every_session_member_the_adapter_uses():
    """The proxy must cover every session member SQLAlchemyUserDatabase touches."""

    missing = sorted(name for name in _session_members_used_by_adapter() if name not in vars(_AsyncSessionProxy))

    assert not missing, (
        f"_AsyncSessionProxy is missing session member(s) {missing} used by SQLAlchemyUserDatabase. "
        "fastapi-users-db-sqlalchemy was probably upgraded - implement them in user/user_stuff.py."
    )


def test_proxy_raises_helpful_error_for_unimplemented_members(db_session):
    """Unimplemented attribute access should raise NotImplementedError with a helpful message."""

    proxy = _AsyncSessionProxy(db_session)

    try:
        proxy.flush
    except NotImplementedError as exc:
        assert "flush" in str(exc)
    else:
        raise AssertionError("Expected NotImplementedError for an unimplemented session member")


def test_adapter_round_trip_through_proxy(db_session):
    """Create, fetch, update and delete a user through the adapter to exercise the proxy for real."""

    user_db = SQLAlchemyUserDatabase[User_DB, int](_AsyncSessionProxy(db_session), User_DB)

    created = asyncio.run(
        user_db.create(
            {
                "email": "proxy@example.com",
                "hashed_password": "not-a-real-hash",
                "first_name": "Proxy",
                "last_name": "User",
                "telephone_number": "0700000000",
            }
        )
    )
    assert created.id is not None

    # get() and get_by_email() both go through _get_user() -> session.execute()
    assert asyncio.run(user_db.get(created.id)).email == "proxy@example.com"
    assert asyncio.run(user_db.get_by_email("PROXY@example.com")).id == created.id

    updated = asyncio.run(user_db.update(created, {"first_name": "Renamed", "is_verified": True}))
    assert updated.first_name == "Renamed"
    assert updated.is_verified is True

    asyncio.run(user_db.delete(updated))
    assert asyncio.run(user_db.get(created.id)) is None
