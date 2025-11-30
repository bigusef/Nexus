"""Integration tests for UserRepository."""

from uuid import uuid4

import pytest

from src.domains.auth.entities import User
from src.domains.auth.repositories import UserRepository
from src.exceptions import NotFoundException


class TestUserRepositorySelectByEmail:
    """Tests for select_by_email method."""

    async def test_select_by_email_found(self, db_session, test_user):
        """Test selecting user by email when found."""
        repo = UserRepository(db_session)

        user = await repo.select_by_email(test_user.email)

        assert user is not None
        assert user.pk == test_user.pk
        assert user.email == test_user.email

    async def test_select_by_email_not_found(self, db_session):
        """Test selecting user by email when not found."""
        repo = UserRepository(db_session)

        user = await repo.select_by_email("nonexistent@example.com")

        assert user is None

    async def test_select_by_email_case_sensitive(self, db_session):
        """Test that email lookup is case-sensitive (depends on DB collation)."""
        repo = UserRepository(db_session)

        await repo.create(
            pk=uuid4(),
            email="CaseSensitive@example.com",
            first_name="Case",
            last_name="Sensitive",
        )

        # Exact match should work
        user = await repo.select_by_email("CaseSensitive@example.com")
        assert user is not None


class TestUserRepositoryGetById:
    """Tests for get_by_id method with UUID."""

    async def test_get_by_id_found(self, db_session, test_user):
        """Test getting user by UUID ID when found."""
        repo = UserRepository(db_session)

        user = await repo.get_by_id(test_user.pk)

        assert user.pk == test_user.pk
        assert user.email == test_user.email

    async def test_get_by_id_not_found(self, db_session):
        """Test getting user by UUID ID when not found."""
        repo = UserRepository(db_session)

        with pytest.raises(NotFoundException):
            await repo.get_by_id(uuid4())


class TestUserEntity:
    """Tests for User entity properties."""

    async def test_full_name(self, test_user):
        """Test full_name property."""
        assert test_user.full_name == f"{test_user.first_name} {test_user.last_name}"

    async def test_is_active_when_not_locked(self, test_user):
        """Test is_active returns True when not locked."""
        assert test_user.is_locked is False
        assert test_user.is_active is True

    async def test_is_active_when_locked(self, locked_user):
        """Test is_active returns False when locked."""
        assert locked_user.is_locked is True
        assert locked_user.is_active is False

    async def test_staff_user(self, staff_user):
        """Test staff user properties."""
        assert staff_user.is_staff is True
        assert staff_user.is_active is True
