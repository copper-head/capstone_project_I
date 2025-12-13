"""Core authentication functions using database connections/cursors.

These functions perform SQL queries for user management.
Assumes a 'users' table with columns: id (serial), username (text), password_hash (text), email (text).
"""

import bcrypt
from psycopg2.extras import RealDictCursor


def hash_password(password: str) -> tuple[str, str]:
    """Hash a password using bcrypt, returning (hash, salt)."""
    salt = bcrypt.gensalt().decode('utf-8')
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt.encode('utf-8')).decode('utf-8')
    return hashed, salt


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


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


# Example usage (not part of the module, just for reference):
# from backend.db.database import pg
# with pg.connection() as conn:
#     user_id = create_user(conn, 'testuser', 'password123', 'test@example.com')
#     user = authenticate_user(conn, 'testuser', 'password123')
#     print(user)