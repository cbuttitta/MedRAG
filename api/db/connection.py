import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db():
    """
    Returns a new psycopg2 connection.
    In a production app you would use a connection pool (e.g. psycopg2.pool).
    For a portfolio project, a new connection per request is acceptable.
    """
    return psycopg2.connect(os.getenv('DATABASE_URL'))

