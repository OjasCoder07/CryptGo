from flask import Flask, request, jsonify
from flask_cors import CORS
from db import get_db_connection
import bcrypt

app = Flask(__name__)
CORS(app)

@app.route("/health", methods=["GET"])
def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT 1;")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return {
            "status": "ok",
            "db_result": result[0]
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }, 500

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE email = %s;", (email,))
    user = cursor.fetchone()

    if user:
        cursor.close()
        conn.close()
        return jsonify({"error": "User already exists"}), 409

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    cursor.execute(
        "INSERT INTO users (email, password_hash) VALUES (%s, %s);",
        (email, hashed_password)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Signup successful"}), 201


if __name__ == "__main__":
    app.run(debug=True)
