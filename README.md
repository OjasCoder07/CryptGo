# CryptGo  
End-to-End Encrypted File Storage System

CryptGo is a Winter of Code (WOC) project focused on understanding
secure authentication, OTP verification, and encrypted file handling.
The main objective of this project is learning security concepts
andn building an end-to-end encrypted file sharing platform.

---

## Project Structure

CryptGo/
│
├── Backend/
│ ├── app.py
│ ├── requirements.txt
│ └── other backend files
│
├── Frontend/
│ ├── signup.html
│ ├── login.html
│ ├── style.css
│ └── script.js
│
├── report.md
├── .env.example
└── README.md

---

## Features
- User signup and login system
- Secure backend-driven authentication
- Encrypted file storage concept
- Use of environment variables for sensitive data
- Separation of frontend and backend

---

## Tech Stack
- Python (Flask)
- HTML, CSS, JavaScript
- PostgreSQL
- SMTP (for OTP emails)

---

## How to Run the Project

### Backend Setup
1. Navigate to the `Backend` folder  
2. Activate the virtual environment
3. Install dependencies:
pip install -r requirements.txt

4. Run the backend server:
python app.py

The backend runs at:
http://127.0.0.1:5000

---

### Frontend Setup
1. Open a terminal in the Frontend folder
2. Start a local server using Python:
python -m http.server 5500

3. Open a browser and go to:
http://127.0.0.1:5500/Cryptgo1.html

⚠️ The frontend will not work unless the backend server is running.

---
## Running Order
1. Start the backend server (`python app.py`)
2. Start the frontend local server (`python -m http.server 5500`)
3. Access the frontend through the browser using the local server URL
---

## Environment Variables

This project uses environment variables for security reasons.
Sensitive information is **not included in the repository**.

Create a `.env` file in the `Backend` folder and add:

EMAIL_USER=your_email_here
EMAIL_PASS=your_email_app_password
DB_PASSWORD=your_postgresql_password

A sample file `.env.example` is provided for reference.

---

## Notes
- This project is part of Winter of Code 8.0
- The repository was initially submitted for mid-evaluation and later updated for final submission
- The project is currently a work in progress with core functionality implemented
- OTP and encryption features demonstrate conceptual understanding
- Some features are partial and intended to demonstrate learning
of authentication and security concepts.
