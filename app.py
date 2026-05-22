from flask import Flask, request
import psycopg2
from datetime import datetime

app = Flask(__name__)

# 🔥 RENDER DATABASE (PASTE YOUR DETAILS HERE)
conn = psycopg2.connect(
    host="YOUR_HOST",
    database="YOUR_DATABASE",
    user="YOUR_USER",
    password="YOUR_PASSWORD",
    port=5432
)

@app.route("/rfid")
def rfid():
    uid_raw = request.args.get("uid")

    if not uid_raw:
        return "NO_UID"

    cursor = conn.cursor()
    time_now = datetime.now().strftime("%H:%M:%S")

    # 🔴 TEMP CARD
    if uid_raw.startswith("temp:"):
        uid = uid_raw.replace("temp:", "")

        cursor.execute("SELECT name, grade FROM temp_cards WHERE uid=%s", (uid,))
        r = cursor.fetchone()

        if r:
            cursor.execute("""
                INSERT INTO attendance (uid,name,grade,time,status,date)
                VALUES (%s,%s,%s,%s,%s,CURRENT_DATE)
            """, (uid, r[0], r[1], time_now, "Temp"))

            conn.commit()
            return "ACCESS_GRANTED"
        else:
            return "TEMP_NOT_FOUND"

    # 🟢 NORMAL CARD
    uid = uid_raw

    cursor.execute("SELECT name, grade FROM students WHERE uid=%s", (uid,))
    r = cursor.fetchone()

    if not r:
        return "ACCESS_DENIED"

    cursor.execute("""
        INSERT INTO attendance (uid,name,grade,time,status,date)
        VALUES (%s,%s,%s,%s,%s,CURRENT_DATE)
    """, (uid, r[0], r[1], time_now, "Present"))

    conn.commit()

    return "ACCESS_GRANTED"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
