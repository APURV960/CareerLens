import os
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
import dotenv

dotenv.load_dotenv()

# Build connection parameters from env or settings
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = f"host=localhost dbname=ai_agent user=postgres password={os.getenv('DB_PASSWORD')}"

# Initialise connection pool for concurrent multi-user threads
_pool = ThreadedConnectionPool(
    minconn=2,
    maxconn=20,
    dsn=DATABASE_URL
)

@contextmanager
def get_db_connection():
    """
    Context manager to fetch database connections from the Threaded pool.
    Commits on success, rolls back on exceptions.
    """
    conn = _pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)
