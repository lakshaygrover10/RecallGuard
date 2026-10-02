from flask import Flask, request, jsonify, send_file
import sqlite3

app = Flask(__name__)


def check_recall(medicine, manufacturer, batch):
    connection = sqlite3.connect("recallguard.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT medicine, manufacturer, batch, reason
        FROM recalls
        WHERE LOWER(TRIM(medicine)) LIKE LOWER(TRIM(?))
        AND LOWER(TRIM(manufacturer)) LIKE LOWER(TRIM(?))
        AND LOWER(TRIM(batch)) = LOWER(TRIM(?))
    """, (
        f"%{medicine}%",
        f"%{manufacturer}%",
        batch
    ))

    result = cursor.fetchone()

    connection.close()

    return result


@app.route("/")
def home():
    return send_file("index.html")


@app.route("/check", methods=["POST"])
def check():
    data = request.json

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
            "medicine": result[0],
            "manufacturer": result[1],
            "batch": result[2],
            "reason": result[3]
        })

    return jsonify({
        "recalled": False
    })


if __name__ == "__main__":
    app.run(debug=True)