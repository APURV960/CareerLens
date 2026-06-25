from backend.repositories.db_pool import get_db_connection

def create_anonymous_user(session_id: str) -> int:
    """Inserts a new anonymous user with a session UUID."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (session_id, is_anonymous) VALUES (%s, TRUE) RETURNING id",
                (session_id,)
            )
            return cur.fetchone()[0]

def get_user_by_session(session_id: str):
    """Retrieves user info corresponding to the session UUID."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, session_id, is_anonymous FROM users WHERE session_id = %s", (session_id,))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "session_id": row[1],
                "is_anonymous": row[2]
            }

def create_registered_user(email: str, hashed_password: str) -> int:
    """Creates a standard registered user (for Mode B JWT auth)."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (email, hashed_password, is_anonymous) VALUES (%s, %s, FALSE) RETURNING id",
                (email, hashed_password)
            )
            return cur.fetchone()[0]

def get_user_by_email(email: str):
    """Retrieves user by registered email address."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, email, hashed_password, is_anonymous FROM users WHERE email = %s", (email,))
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "email": row[1],
                "hashed_password": row[2],
                "is_anonymous": row[3]
            }

def link_session_to_user(session_id: str, user_id: int):
    """Updates anonymous database records to link to a registered account."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE users SET session_id = %s WHERE id = %s", (session_id, user_id))
