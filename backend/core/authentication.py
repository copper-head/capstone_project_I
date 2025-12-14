"""Core authentication functions using database connections/cursors.

These functions perform SQL queries for user management.
Assumes a 'users' table with columns: id (serial), username (text), password_hash (text), email (text).
"""

import bcrypt
import secrets
from datetime import datetime, timedelta, timezone
from psycopg2.extras import RealDictCursor


def hash_password(password: str) -> tuple[str, str]:
    """Hash a password using bcrypt, returning (hash, salt)."""
    salt = bcrypt.gensalt().decode('utf-8')
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8')).decode('utf-8')
    return hashed, salt


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def get_token(conn, user_id: int, ttl_minutes: int = 60) -> str:
    """Issue a new opaque access token for a user and persist it.

    Args:
        conn: psycopg2 connection.
        user_id: ID of the user to issue the token for.
        ttl_minutes: Token time-to-live in minutes.

    Returns:
        The newly created token string.
    """
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=ttl_minutes)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO tokens (user_id, token, expires_at) VALUES (%s, %s, %s)",
            (user_id, token, expires_at)
        )
        conn.commit()
    return token


def verify_token(conn, token: str) -> dict | None:
    """Verify an opaque token against the DB and expiration.

    Args:
        conn: psycopg2 connection.
        token: Token string to validate.

    Returns:
        A user dict (id, username, email) if valid, else None.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT u.id, u.username, u.email, t.expires_at
            FROM tokens t
            JOIN users u ON u.id = t.user_id
            WHERE t.token = %s
            """,
            (token,)
        )
        row = cur.fetchone()
        if not row:
            return None
        # Check expiration
        expires_at = row.get("expires_at")
        now = datetime.now(timezone.utc)
        if expires_at is None or expires_at.tzinfo is None:
            # Treat naive timestamps as UTC
            expires_at = expires_at.replace(tzinfo=timezone.utc) if expires_at else now
        if now >= expires_at:
            # Optionally delete expired token
            cur.execute("DELETE FROM tokens WHERE token = %s", (token,))
            conn.commit()
            return None
        # Return user fields
        return {"id": row["id"], "username": row["username"], "email": row["email"]}


def create_user(conn, username: str, password: str, email: str = None) -> int:
    """Create a new user in the database.

    Args:
        conn: Database connection object.
        username: Unique username.
        password: Plain text password (will be hashed).
        email: Optional email.

    Returns:
        The new user's ID.

    Raises:
        Exception if username already exists or other DB error.
    """
    hashed, salt = hash_password(password)
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "INSERT INTO users (username, password_hash, password_salt, email) VALUES (%s, %s, %s, %s) RETURNING id",
            (username, hashed, salt, email)
        )
        result = cur.fetchone()
        conn.commit()
        return result['id'] if result else None


def authenticate_user(conn, username: str, password: str) -> dict:
    """Authenticate a user by username and password.

    Args:
        conn: Database connection object.
        username: Username to check.
        password: Plain text password.

    Returns:
        User dict if authenticated, else None.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT id, username, password_hash, email FROM users WHERE username = %s",
            (username,)
        )
        user = cur.fetchone()
        if user and verify_password(password, user['password_hash']):
            # Remove password_hash from response
            user.pop('password_hash', None)
            return user
        return None


def get_user_by_id(conn, user_id: int) -> dict:
    """Get user details by ID.

    Args:
        conn: Database connection object.
        user_id: User ID.

    Returns:
        User dict or None.
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
        return cur.fetchone()


def update_user_email(conn, user_id: int, new_email: str) -> bool:
    """Update a user's email.

    Args:
        conn: Database connection object.
        user_id: User ID.
        new_email: New email address.

    Returns:
        True if updated, False otherwise.
    """
    with conn.cursor() as cur:
        cur.execute("UPDATE users SET email = %s WHERE id = %s", (new_email, user_id))
        conn.commit()
        return cur.rowcount > 0


def delete_user(conn, user_id: int) -> bool:
    """Delete a user by ID.

    Args:
        conn: Database connection object.
        user_id: User ID.

    Returns:
        True if deleted, False otherwise.
    """
    with conn.cursor() as cur:
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return cur.rowcount > 0