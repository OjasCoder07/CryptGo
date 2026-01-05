from flask import Flask, request, jsonify, session, send_file
from flask_cors import CORS
from db import get_db_connection
import bcrypt
import random
import datetime
from werkzeug.utils import secure_filename
from auth import hash_password, verify_password
from crypto import decrypt_data, derive_key, encrypt_data
import io
import os
from storage import save_file

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5500"])
app.secret_key = os.getenv("FLASK_SECRET_KEY")

app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True
)


def log_action(user_id, action, details):
    conn = get_db_connection()
    cur = conn.cursor()

    now = datetime.datetime.utcnow()

    cur.execute(
        "INSERT INTO audit_logs (user_id, action, details, timestamp) VALUES (%s, %s, %s, %s)",
        (user_id, action, details, now)
    )
    conn.commit()
    cur.close()
    conn.close()

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

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, password_hash FROM users WHERE email = %s;",
        (email,)
    )
    user = cursor.fetchone()

    if not user:
        cursor.close()
        conn.close()
        return jsonify({"error": "Invalid credentials"}), 401

    user_id, password_hash = user

    if not bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
        cursor.close()
        conn.close()
        return jsonify({"error": "Invalid credentials"}), 401

    cursor.execute(
        "DELETE FROM mfa_otps WHERE user_id = %s;",
        (user_id,)
    )

    otp = str(random.randint(100000, 999999))
    otp_hash = bcrypt.hashpw(otp.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)

    cursor.execute(
        """
        INSERT INTO mfa_otps (user_id, otp_hash, expires_at, is_used)
        VALUES (%s, %s, %s, FALSE);
        """,
        (user_id, otp_hash, expires_at)
    )

    conn.commit()
    cursor.close()
    conn.close()

    session.clear()
    session["pending_user"] = user_id

    return jsonify({
        "message": "OTP generated",
        "otp": otp
    }), 200



@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.get_json()
    otp_entered = data.get("otp")

    user_id = session.get("pending_user")
    if user_id is None:
        return jsonify({"error": "Session expired"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, otp_hash, expires_at
        FROM mfa_otps
        WHERE user_id = %s AND is_used = FALSE
        ORDER BY id DESC
        LIMIT 1;
        """,
        (user_id,)
    )

    record = cursor.fetchone()

    if not record:
        cursor.close()
        conn.close()
        return jsonify({"error": "OTP not found"}), 401

    otp_id, otp_hash, expires_at = record

    if datetime.datetime.utcnow() > expires_at.replace(tzinfo=None):
        cursor.close()
        conn.close()
        return jsonify({"error": "OTP expired"}), 401

    if not bcrypt.checkpw(otp_entered.encode("utf-8"), otp_hash.encode("utf-8")):
        cursor.close()
        conn.close()
        return jsonify({"error": "Invalid OTP"}), 401

    cursor.execute(
        "UPDATE mfa_otps SET is_used = TRUE WHERE id = %s;",
        (otp_id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    log_action(user_id, "LOGIN_SUCCESS", "User successfully verified MFA code.")

    session.clear()
    session["user_id"] = user_id

    return jsonify({"message": "Login successful"}), 200

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200

@app.route("/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"authenticated": False}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT is_admin FROM users WHERE id = %s;", (session["user_id"],))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if not result:
        return jsonify({"authenticated": False, "error": "User not found"}), 404

    return jsonify({
        "authenticated": True,
        "user_id": session["user_id"],
        "is_admin": result[0]
    }), 200


@app.route("/upload", methods=["POST"])
def upload():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    file = request.files.get("file")
    if not file:
        return jsonify({"error": "No file"}), 400

    filename = secure_filename(file.filename)
    encrypted_data = file.read()

    try:
        save_file(session["user_id"], filename, encrypted_data)
        log_action(session['user_id'], "FILE_UPLOAD", f"Uploaded {filename}")
        return jsonify({"message": "File uploaded successfully"}), 200
    except Exception as e:
        print("Upload Error:", e)  # Check your terminal for this!
        return jsonify({"error": str(e)}), 500


@app.route("/files", methods=["GET"])
def list_files():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cur = conn.cursor()
    # Ensure your DB table has 'uploaded_at' column or remove it from query
    cur.execute("SELECT id, filename, uploaded_at FROM files WHERE user_id = %s ORDER BY id DESC",
                (session["user_id"],))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    files = [{"id": r[0], "filename": r[1], "uploaded_at": str(r[2])} for r in rows]
    return jsonify(files), 200


@app.route("/download/<int:file_id>", methods=["GET"])
def download_file(file_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT filename, path FROM files WHERE id=%s AND user_id=%s", (file_id, session["user_id"]))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return jsonify({"error": "File not found"}), 404

    filename, path = row
    log_action(session['user_id'], "FILE_DOWNLOAD", f"Accessed {filename}")
    return send_file(path, as_attachment=True, download_name=filename)


@app.route("/delete/<int:file_id>", methods=["DELETE"])
def delete_file(file_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT path FROM files WHERE id=%s AND user_id=%s", (file_id, session["user_id"]))
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        return jsonify({"error": "File not found"}), 404

    file_path = row[0]

    cur.execute("DELETE FROM files WHERE id=%s", (file_id,))

    if os.path.exists(file_path):
        os.remove(file_path)

    conn.commit()
    cur.close()
    conn.close()
    log_action(session['user_id'], "FILE_DELETE", f"Deleted file ID {file_id}")
    return jsonify({"message": "File deleted successfully"}), 200


@app.route("/admin/logs", methods=["GET"])
def get_admin_logs():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db_connection()
    cur = conn.cursor()

    # Check if user is admin
    cur.execute("SELECT is_admin FROM users WHERE id = %s", (session["user_id"],))
    user = cur.fetchone()

    if not user or not user[0]:
        cur.close()
        conn.close()
        return jsonify({"error": "Forbidden"}), 403

    # Fetch logs
    cur.execute(
        "SELECT u.email, a.action, a.details, a.timestamp FROM audit_logs a JOIN users u ON a.user_id = u.id ORDER BY a.timestamp DESC")
    rows = cur.fetchall()

    logs = [{"email": r[0], "action": r[1], "details": r[2], "timestamp": r[3].strftime("%Y-%m-%d %H:%M:%S")} for r in
            rows]

    cur.close()
    conn.close()
    return jsonify(logs)


if __name__ == "__main__":
    app.run(debug=True)