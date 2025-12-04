"""Authentication domain repositories."""

from uuid import UUID

from src.abstract import Repository

from .entities import User


class UserRepository(Repository[User]):
    """Repository for User entity operations.

    Provides standard CRUD operations plus domain-specific queries.
    """

    async def get_by_id(self, pk: UUID) -> User:
        """Get a User by primary key, raise if not found.

        Args:
            pk: Primary key value.

        Returns:
            The matching entity.

        Raises:
            NotFoundException: If no entity matches the primary key.

        Example:
            user = await repo.get_by_id(user_id)
        """
        return await self.get_one(User.pk == pk)

    async def select_by_email(self, email: str) -> User | None:
        """Get user by email address.

        Args:
            email: User's email address.

        Returns:
            User if found, None otherwise.
        """
        return await self.select_one(User.email == email)
