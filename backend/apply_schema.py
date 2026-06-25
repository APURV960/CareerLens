import os
from dotenv import load_dotenv

from backend.repositories.db_pool import get_db_connection

load_dotenv()


def apply_schema():
    print("Connecting to database...")

    schema_path = os.path.join(
        os.path.dirname(__file__),
        "schema.sql"
    )

    print(f"Reading schema from {schema_path}...")

    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()

    with get_db_connection() as conn:
        cur = conn.cursor()

        print("Dropping existing tables...")

        try:
            cur.execute("""
                DROP TABLE IF EXISTS
                    applications,
                    cover_letters,
                    skill_gaps,
                    job_results,
                    search_runs,
                    agent_jobs,
                    resumes,
                    users
                CASCADE;
            """)
            print("Dropped old tables.")
        except Exception as e:
            print("Drop failed:", e)

        print("Applying schema...")

        cur.execute(sql)

        cur.close()

    print("Database schema configured successfully!")


if __name__ == "__main__":
    apply_schema()