import os
import threading
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
import dotenv

dotenv.load_dotenv()

# Build connection parameters from env or settings
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = f"host=localhost dbname=ai_agent user=postgres password={os.getenv('DB_PASSWORD')}"

_pool = None
_pool_lock = threading.Lock()

def _get_pool():
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                print("[DATABASE] Creating ThreadedConnectionPool lazily...")
                try:
                    _pool = ThreadedConnectionPool(
                        minconn=2,
                        maxconn=20,
                        dsn=DATABASE_URL
                    )
                    print("[DATABASE] ThreadedConnectionPool initialized successfully.")
                except Exception as e:
                    print(f"[DATABASE] CRITICAL ERROR: Failed to initialize ThreadedConnectionPool: {e}")
                    raise
    return _pool

@contextmanager
def get_db_connection():
    """
    Context manager to fetch database connections from the Threaded pool.
    Commits on success, rolls back on exceptions.
    """
    pool = _get_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        pool.putconn(conn)

