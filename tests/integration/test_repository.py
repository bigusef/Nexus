"""Integration tests for base Repository class."""

from uuid import uuid4

import pytest

from src.domains.auth.entities import User
from src.domains.auth.repositories import UserRepository
from src.exceptions import NotFoundException


class TestRepositoryCreate:
    """Tests for repository create operations."""

    async def test_create(self, db_session):
        """Test creating a single entity."""
        repo = UserRepository(db_session)
        user = await repo.create(
            pk=uuid4(),
            email="create@example.com",
            first_name="Create",
            last_name="Test",
        )

        assert user.pk is not None
        assert user.email == "create@example.com"
        assert user.first_name == "Create"
        assert user.last_name == "Test"

    async def test_create_from_entity(self, db_session):
        """Test creating from an existing entity instance."""
        repo = UserRepository(db_session)
        user = User(
            pk=uuid4(),
            email="entity@example.com",
            first_name="Entity",
            last_name="Test",
        )

        created = await repo.create_from_entity(user)

        assert created.pk == user.pk
        assert created.email == "entity@example.com"

    async def test_bulk_create(self, db_session):
        """Test bulk creating entities."""
        repo = UserRepository(db_session)
        users_data = [
            {"pk": uuid4(), "email": "bulk1@example.com", "first_name": "Bulk1", "last_name": "Test"},
            {"pk": uuid4(), "email": "bulk2@example.com", "first_name": "Bulk2", "last_name": "Test"},
            {"pk": uuid4(), "email": "bulk3@example.com", "first_name": "Bulk3", "last_name": "Test"},
        ]

        users = await repo.bulk_create(users_data)

        assert len(users) == 3
        assert all(u.pk is not None for u in users)


class TestRepositoryRead:
    """Tests for repository read operations."""

    async def test_get_one(self, db_session, test_user):
        """Test getting a single entity."""
        repo = UserRepository(db_session)
        user = await repo.get_one(User.pk == test_user.pk)

        assert user.pk == test_user.pk
        assert user.email == test_user.email

    async def test_get_one_not_found(self, db_session):
        """Test get_one raises NotFoundException."""
        repo = UserRepository(db_session)

        with pytest.raises(NotFoundException):
            await repo.get_one(User.pk == uuid4())

    async def test_select_one(self, db_session, test_user):
        """Test selecting a single entity."""
        repo = UserRepository(db_session)
        user = await repo.select_one(User.pk == test_user.pk)

        assert user is not None
        assert user.pk == test_user.pk

    async def test_select_one_not_found(self, db_session):
        """Test select_one returns None when not found."""
        repo = UserRepository(db_session)
        user = await repo.select_one(User.pk == uuid4())

        assert user is None

    async def test_get_by_id(self, db_session, test_user):
        """Test getting by primary key."""
        repo = UserRepository(db_session)
        user = await repo.get_by_id(test_user.pk)

        assert user.pk == test_user.pk

    async def test_select_all(self, db_session):
        """Test selecting all entities."""
        repo = UserRepository(db_session)

        # Create some users
        await repo.create(pk=uuid4(), email="all1@example.com", first_name="All1", last_name="Test")
        await repo.create(pk=uuid4(), email="all2@example.com", first_name="All2", last_name="Test")

        users = await repo.select_all()

        assert len(users) >= 2

    async def test_select_all_with_filter(self, db_session):
        """Test selecting all with filter."""
        repo = UserRepository(db_session)

        await repo.create(pk=uuid4(), email="staff1@example.com", first_name="Staff1", last_name="Test", is_staff=True)
        await repo.create(pk=uuid4(), email="regular1@example.com", first_name="Regular1", last_name="Test", is_staff=False)

        staff_users = await repo.select_all(User.is_staff == True)

        assert all(u.is_staff for u in staff_users)

    async def test_paginate(self, db_session):
        """Test pagination."""
        repo = UserRepository(db_session)

        # Create multiple users
        for i in range(5):
            await repo.create(pk=uuid4(), email=f"page{i}@example.com", first_name=f"Page{i}", last_name="Test")

        users, total = await repo.paginate(limit=2, offset=0)

        assert len(users) == 2
        assert total >= 5

    async def test_get_by_ids(self, db_session):
        """Test getting multiple by IDs."""
        repo = UserRepository(db_session)

        user1 = await repo.create(pk=uuid4(), email="ids1@example.com", first_name="Ids1", last_name="Test")
        user2 = await repo.create(pk=uuid4(), email="ids2@example.com", first_name="Ids2", last_name="Test")

        users = await repo.get_by_ids([user1.pk, user2.pk])

        assert len(users) == 2

    async def test_get_by_ids_empty(self, db_session):
        """Test get_by_ids with empty list."""
        repo = UserRepository(db_session)
        users = await repo.get_by_ids([])

        assert users == []


class TestRepositoryUpdate:
    """Tests for repository update operations."""

    async def test_update(self, db_session, test_user):
        """Test updating a single entity."""
        repo = UserRepository(db_session)
        updated = await repo.update(test_user, first_name="Updated")

        assert updated.first_name == "Updated"

    async def test_update_by_filters(self, db_session):
        """Test updating by filters."""
        repo = UserRepository(db_session)

        user = await repo.create(pk=uuid4(), email="filter_update@example.com", first_name="Before", last_name="Test")

        count = await repo.update_by_filters(
            {"first_name": "After"},
            User.email == "filter_update@example.com",
        )

        assert count == 1

    async def test_bulk_update(self, db_session):
        """Test bulk updating entities."""
        repo = UserRepository(db_session)

        user1 = await repo.create(pk=uuid4(), email="bulkup1@example.com", first_name="Bulk1", last_name="Test")
        user2 = await repo.create(pk=uuid4(), email="bulkup2@example.com", first_name="Bulk2", last_name="Test")

        updated = await repo.bulk_update([user1, user2], {"last_name": "Updated"})

        assert all(u.last_name == "Updated" for u in updated)


class TestRepositoryDelete:
    """Tests for repository delete operations."""

    async def test_delete(self, db_session):
        """Test deleting a single entity."""
        repo = UserRepository(db_session)
        user = await repo.create(pk=uuid4(), email="delete@example.com", first_name="Delete", last_name="Test")

        await repo.delete(user)

        result = await repo.select_one(User.email == "delete@example.com")
        assert result is None

    async def test_delete_by_filters(self, db_session):
        """Test deleting by filters."""
        repo = UserRepository(db_session)
        await repo.create(pk=uuid4(), email="filter_del@example.com", first_name="FilterDel", last_name="Test")

        count = await repo.delete_by_filters(User.email == "filter_del@example.com")

        assert count == 1

    async def test_delete_by_filters_requires_filter(self, db_session):
        """Test that delete_by_filters requires at least one filter."""
        repo = UserRepository(db_session)

        with pytest.raises(ValueError, match="At least one filter is required"):
            await repo.delete_by_filters()

    async def test_bulk_delete(self, db_session):
        """Test bulk deleting entities."""
        repo = UserRepository(db_session)

        user1 = await repo.create(pk=uuid4(), email="bulkdel1@example.com", first_name="BulkDel1", last_name="Test")
        user2 = await repo.create(pk=uuid4(), email="bulkdel2@example.com", first_name="BulkDel2", last_name="Test")

        await repo.bulk_delete([user1, user2])

        result1 = await repo.select_one(User.email == "bulkdel1@example.com")
        result2 = await repo.select_one(User.email == "bulkdel2@example.com")

        assert result1 is None
        assert result2 is None


class TestRepositoryCountExists:
    """Tests for repository count and exists operations."""

    async def test_count(self, db_session):
        """Test counting entities."""
        repo = UserRepository(db_session)

        await repo.create(pk=uuid4(), email="count1@example.com", first_name="Count1", last_name="Test")
        await repo.create(pk=uuid4(), email="count2@example.com", first_name="Count2", last_name="Test")

        count = await repo.count()

        assert count >= 2

    async def test_count_with_filter(self, db_session):
        """Test counting with filter."""
        repo = UserRepository(db_session)

        await repo.create(pk=uuid4(), email="countstaff@example.com", first_name="Staff", last_name="Test", is_staff=True)

        count = await repo.count(User.is_staff == True)

        assert count >= 1

    async def test_exists(self, db_session, test_user):
        """Test checking existence."""
        repo = UserRepository(db_session)

        exists = await repo.exists(User.pk == test_user.pk)

        assert exists is True

    async def test_exists_not_found(self, db_session):
        """Test exists returns False when not found."""
        repo = UserRepository(db_session)

        exists = await repo.exists(User.pk == uuid4())

        assert exists is False
