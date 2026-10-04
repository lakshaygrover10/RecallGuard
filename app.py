from flask import Flask, request, jsonify, send_file, redirect, session
import sqlite3
from functools import wraps

app = Flask(__name__)

# =========================
# SESSION SECURITY
# =========================

app.secret_key = "recallguard-secret-key"


# =========================
# DATABASE
# =========================

def get_db():

    connection = sqlite3.connect("recallguard.db")

    connection.row_factory = sqlite3.Row

    return connection


# =========================
# LOGIN PROTECTION
# =========================

def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if not session.get("logged_in"):
            return redirect("/login")

        return function(*args, **kwargs)

    return wrapper


# =========================
# RECALL MATCHING
# =========================

def check_recall(medicine, manufacturer, batch):

    connection = get_db()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            medicine,
            manufacturer,
            batch,
            reason
        FROM recalls
        WHERE LOWER(TRIM(medicine))
            LIKE LOWER(TRIM(?))

        AND LOWER(TRIM(manufacturer))
            LIKE LOWER(TRIM(?))

        AND LOWER(TRIM(batch))
            = LOWER(TRIM(?))
    """, (

        f"%{medicine}%",
        f"%{manufacturer}%",
        batch

    ))

    result = cursor.fetchone()

    connection.close()

    return result


# =========================
# WELCOME PAGE
# =========================

@app.route("/")
def welcome():

    return send_file("welcome.html")


# =========================
# LOGIN PAGE
# =========================

@app.route("/login", methods=["GET"])
def login_page():

    if session.get("logged_in"):

        return redirect("/dashboard")

    return send_file("login.html")


# =========================
# LOGIN API
# =========================

@app.route("/login", methods=["POST"])
def login():

    data = request.json or {}

    email = data.get("email", "").strip()

    password = data.get("password", "")


    # DEMO LOGIN

    if (
        email == "admin@recallguard.com"
        and password == "admin123"
    ):

        session["logged_in"] = True

        session["user_email"] = email

        return jsonify({
            "success": True
        })


    return jsonify({
        "success": False,
        "message": "Invalid email or password."
    }), 401


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
@login_required
def dashboard():

    return send_file("index.html")


# =========================
# LOGO
# =========================

@app.route("/logo.png")
def logo():

    return send_file("logo.png")


# =========================
# CHECK MEDICINE BATCH
# =========================

@app.route("/check", methods=["POST"])
@login_required
def check():

    data = request.json or {}

    medicine = data.get("medicine", "")

    manufacturer = data.get("manufacturer", "")

    batch = data.get("batch", "")


    result = check_recall(
        medicine,
        manufacturer,
        batch
    )


    if result:

        return jsonify({

            "recalled": True,

            "medicine": result["medicine"],

            "manufacturer": result["manufacturer"],

            "batch": result["batch"],

            "reason": result["reason"]

        })


    return jsonify({

        "recalled": False

    })


# =========================
# DASHBOARD DATA
# =========================

@app.route("/dashboard-data")
@login_required
def dashboard_data():

    connection = get_db()

    cursor = connection.cursor()


    # Total records

    cursor.execute("""
        SELECT COUNT(*)
        FROM recalls
    """)

    total_records = cursor.fetchone()[0]


    # Manufacturers

    cursor.execute("""
        SELECT COUNT(DISTINCT manufacturer)
        FROM recalls
    """)

    manufacturers = cursor.fetchone()[0]


    # Recent alerts

    cursor.execute("""
        SELECT
            medicine,
            manufacturer,
            batch,
            reason
        FROM recalls
        ORDER BY rowid DESC
        LIMIT 5
    """)

    recent = [

        dict(row)

        for row in cursor.fetchall()

    ]


    # All records

    cursor.execute("""
        SELECT
            medicine,
            manufacturer,
            batch,
            reason,
            manufacture_date,
            expiry_date,
            reported_by
        FROM recalls
        ORDER BY rowid DESC
    """)

    records = [

        dict(row)

        for row in cursor.fetchall()

    ]


    connection.close()


    return jsonify({

        "total_records": total_records,

        "manufacturers": manufacturers,

        "alerts": total_records,

        "recent": recent,

        "records": records

    })


# =========================
# RUN APP
# =========================

if __name__ == "__main__":

    app.run(debug=True)