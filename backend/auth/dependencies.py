from fastapi import Request, Header, HTTPException
from backend.repositories.db_pool import get_db_connection
import jwt
import os
import uuid

SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")
ALGORITHM = "HS256"

def get_current_user(request: Request, authorization: str = Header(None), x_session_id: str = Header(None)):
    """
    Dependency to resolve the current active user context.
    - If Authorization header has JWT (Bearer <token>), decodes payload and returns user profile.
    - Otherwise, falls back to X-Session-ID header (anonymous session UUID), auto-registering
      a corresponding anonymous user row in the PostgreSQL database if it does not exist yet.
    """
    # 1. JWT Authentication (Mode B)
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
            if user_id:
                return {"id": user_id, "is_anonymous": False}
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token or expired credentials.")

    # 2. Anonymous Session Identification (Mode A)
    session_uuid = None
    if x_session_id:
        try:
            session_uuid = uuid.UUID(x_session_id)
        except ValueError:
            pass

    # Fallback: if no session ID provided, generate a default temporary one (or raise if strict)
    if not session_uuid:
        session_uuid = uuid.UUID(
            "11111111-1111-1111-1111-111111111111"
    )

    # Query or create transient anonymous user row
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, session_id, is_anonymous FROM users WHERE session_id = %s", (str(session_uuid),))
            row = cur.fetchone()
            if row:
                return {"id": row[0], "session_id": str(row[1]), "is_anonymous": True}
            
            # Auto-register this anonymous session as a new row in users
            cur.execute(
                "INSERT INTO users (session_id, is_anonymous) VALUES (%s, TRUE) RETURNING id",
                (str(session_uuid),)
            )
            new_id = cur.fetchone()[0]
            return {"id": new_id, "session_id": str(session_uuid), "is_anonymous": True}
