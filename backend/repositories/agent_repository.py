from backend.repositories.db_pool import get_db_connection

def create_agent_job(job_id: str, user_id: int, status: str = "queued") -> None:
    """Inserts a new agent job tracking record in queued status."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO agent_jobs (id, user_id, status) VALUES (%s, %s, %s)",
                (job_id, user_id, status)
            )

def get_agent_job(job_id: str, user_id: int) -> dict:
    """Retrieves the status and error message of an agent job."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT status, error_message FROM agent_jobs WHERE id = %s AND user_id = %s",
                (job_id, user_id)
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "status": row[0],
                "error_message": row[1]
            }

def update_agent_job_status(job_id: str, status: str, completed_at=None, error_message=None) -> None:
    """Updates the execution status of an agent job (e.g. running, completed, failed)."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if completed_at:
                cur.execute(
                    "UPDATE agent_jobs SET status = %s, completed_at = %s, error_message = %s WHERE id = %s",
                    (status, completed_at, error_message, job_id)
                )
            else:
                cur.execute(
                    "UPDATE agent_jobs SET status = %s WHERE id = %s",
                    (status, job_id)
                )
