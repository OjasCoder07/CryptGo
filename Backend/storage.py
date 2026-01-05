import os
from db import get_db_connection

UPLOAD_DIR = "uploads"

def save_file(user_id, filename, encrypted_data):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as f:
        f.write(encrypted_data)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO files (user_id, filename, path) VALUES (%s, %s, %s)",
        (user_id, filename, path)
    )
    conn.commit()
    cur.close()
    conn.close()
