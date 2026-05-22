import psycopg2
from config.settings import DB_CONFIG

def get_connection():
    try:
        conn = psycopg2.connect(
            **DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None
    