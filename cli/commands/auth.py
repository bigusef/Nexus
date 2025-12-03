"""Authentication management commands."""

import asyncio
import re
from typing import Annotated

import redis.asyncio as aioredis
import typer

from src.core.database import close_database
from src.core.database import get_session_context
from src.core.database import init_database
from src.security import JWTService
from src.core.redis import close_redis
from src.core.redis import init_redis
from src.core.redis import redis_pool
from src.domains.auth.entities import User
from src.domains.auth.repositories import UserRepository


app = typer.Typer(no_args_is_help=True)

# Email validation regex pattern
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


async def _init_services() -> None:
    """Initialize database and redis connections."""
    await init_database()
    await init_redis()


async def _close_services() -> None:
    """Close database and redis connections."""
    await close_database()
    await close_redis()


def _is_valid_email(email: str) -> bool:
    """Validate email format."""
    return EMAIL_PATTERN.match(email) is not None


async def _check_email_exists(email: str) -> bool:
    """Check if email already exists in database."""
    async with get_session_context() as session:
        repo = UserRepository(session)
        user = await repo.select_by_email(email)
        return user is not None


async def _create_user(email: str, first_name: str, last_name: str, is_staff: bool) -> User:
    """Create a new user in the database."""
    async with get_session_context() as session:
        repo = UserRepository(session)
        user = await repo.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=is_staff,
        )
        await session.commit()
        return user


async def _get_user_by_email(email: str) -> User | None:
    """Get user by email."""
    async with get_session_context() as session:
        repo = UserRepository(session)
        return await repo.select_by_email(email)


async def _update_user_lock_status(user: User, is_locked: bool) -> None:
    """Update user lock status."""
    async with get_session_context() as session:
        repo = UserRepository(session)
        await repo.update(user, is_locked=is_locked)
        await session.commit()


async def _generate_tokens(user: User) -> tuple[str, str]:
    """Generate JWT token pair for user."""
    redis_client = aioredis.Redis(connection_pool=redis_pool)
    try:
        jwt_service = JWTService(redis_client)
        token_pair = await jwt_service.create_token_pair(
            user_id=user.pk,
            email=user.email,
            is_staff=user.is_staff,
        )
        return token_pair.access, token_pair.refresh
    finally:
        await redis_client.aclose()


async def _revoke_all_user_tokens(user: User) -> None:
    """Revoke all tokens for a user (logout from all devices)."""
    redis_client = aioredis.Redis(connection_pool=redis_pool)
    try:
        jwt_service = JWTService(redis_client)
        await jwt_service.revoke_all_user_tokens(user.pk)
    finally:
        await redis_client.aclose()


def _prompt_email() -> str:
    """Prompt for email with format validation and uniqueness check."""
    while True:
        email = typer.prompt("Email")

        # Validate email format
        if not _is_valid_email(email):
            typer.echo("Invalid email format. Please enter a valid email address.", err=True)
            continue

        # Check if email already exists
        if asyncio.run(_check_email_exists(email)):
            typer.echo(f"Email '{email}' already exists. Please enter a different email.", err=True)
            continue

        return email


@app.command()
def create(
    staff: Annotated[bool, typer.Option("--staff", help="Create user as staff member")] = False,
) -> None:
    """Create a new user interactively."""
    asyncio.run(_init_services())

    try:
        # Get user details interactively
        email = _prompt_email()
        first_name = typer.prompt("First name")
        last_name = typer.prompt("Last name")

        # Create user
        user = asyncio.run(_create_user(email, first_name, last_name, staff))

        typer.echo("\nUser created successfully!")
        typer.echo(f"  ID: {user.pk}")
        typer.echo(f"  Email: {user.email}")
        typer.echo(f"  Name: {user.full_name}")
        typer.echo(f"  Staff: {user.is_staff}")
    finally:
        asyncio.run(_close_services())


@app.command()
def lock(
    email: Annotated[str, typer.Argument(help="Email of the user to lock")],
) -> None:
    """Lock a user account."""
    asyncio.run(_init_services())

    try:
        user = asyncio.run(_get_user_by_email(email))

        if user is None:
            typer.echo(f"User with email '{email}' not found.", err=True)
            raise typer.Exit(1)

        if user.is_locked:
            typer.echo(f"User '{email}' is already locked.")
            return

        asyncio.run(_update_user_lock_status(user, is_locked=True))
        asyncio.run(_revoke_all_user_tokens(user))
        typer.echo(f"User '{email}' has been locked and logged out from all devices.")
    finally:
        asyncio.run(_close_services())


@app.command()
def unlock(
    email: Annotated[str, typer.Argument(help="Email of the user to unlock")],
) -> None:
    """Unlock a user account."""
    asyncio.run(_init_services())

    try:
        user = asyncio.run(_get_user_by_email(email))

        if user is None:
            typer.echo(f"User with email '{email}' not found.", err=True)
            raise typer.Exit(1)

        if not user.is_locked:
            typer.echo(f"User '{email}' is not locked.")
            return

        asyncio.run(_update_user_lock_status(user, is_locked=False))
        typer.echo(f"User '{email}' has been unlocked.")
    finally:
        asyncio.run(_close_services())


@app.command(name="generate-token")
def generate_token(
    email: Annotated[str, typer.Argument(help="Email of the user to generate tokens for")],
) -> None:
    """Generate JWT token pair for a user."""
    asyncio.run(_init_services())

    try:
        user = asyncio.run(_get_user_by_email(email))

        if user is None:
            typer.echo(f"User with email '{email}' not found.", err=True)
            raise typer.Exit(1)

        if not user.is_active:
            typer.echo(f"User '{email}' is not active (locked).", err=True)
            raise typer.Exit(1)

        access_token, refresh_token = asyncio.run(_generate_tokens(user))

        typer.echo(f"\nTokens generated for user '{email}':\n")
        typer.echo(f"Access Token:\n{access_token}\n")
        typer.echo(f"Refresh Token:\n{refresh_token}")
    finally:
        asyncio.run(_close_services())
