import psycopg2
import os

DB_HOST = "localhost"
DB_NAME = "cryptgo"
DB_USER = "postgres"
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = 5432


def get_db_connection():
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return connection
