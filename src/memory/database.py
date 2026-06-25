# import psycopg2
# import os
# import dotenv
# from backend.repositories.db_pool import get_db_connection
# dotenv.load_dotenv()


# def get_connection():

#     return psycopg2.connect(
#         host="localhost",
#         database="ai_agent",
#         user="postgres",
#         password=os.getenv("DB_PASSWORD")
#     )


from backend.repositories.db_pool import get_db_connection


def get_connection():
    """
    Compatibility wrapper.
    Returns a pooled PostgreSQL connection.
    """
    return get_db_connection()