"""Test factories for generating test data."""

import uuid

import factory

from src.domains.auth.entities import User
from src.utilities.enums import Language


class UserFactory(factory.Factory):
    """Factory for creating User instances."""

    class Meta:
        model = User

    pk = factory.LazyFunction(uuid.uuid4)
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    avatar_url = None
    language = Language.EN
    is_staff = False
    is_locked = False


class StaffUserFactory(UserFactory):
    """Factory for creating staff User instances."""

    email = factory.Sequence(lambda n: f"staff{n}@example.com")
    is_staff = True


class LockedUserFactory(UserFactory):
    """Factory for creating locked User instances."""

    email = factory.Sequence(lambda n: f"locked{n}@example.com")
    is_locked = True
