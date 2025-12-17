import psycopg2

# Database configuration
DB_HOST = "localhost"
DB_NAME = "cryptgo"
DB_USER = "postgres"
DB_PASSWORD = "Mazhi3bai#"
DB_PORT = 5432


def get_db_connection():
    """
    Creates and returns a new database connection.
    """
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )
    return connection
