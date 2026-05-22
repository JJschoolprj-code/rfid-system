from flask import Flask, request
import mysql.connector
from datetime import datetime

app = Flask(__name__)

# 🔥 DATABASE CONFIG (CHANGE THESE)
db = mysql.connector.connect(
    host="sql112.infinityfree.com",
    user="if0_41921723",
    password="AWrnaWgZ1KlW",
    database="if0_41921723_rfid_system"
)

@app.route("/rfid")
def rfid():
    uid_raw = request.args.get("uid")

    if not uid_raw:
        return "NO_UID"

    cursor = db.cursor(dictionary=True)
    time_now = datetime.now().strftime("%H:%M:%S")

    # 🔴 TEMP CARD
    if uid_raw.startswith("temp:"):
        uid = uid_raw.replace("temp:", "")

        cursor.execute("SELECT * FROM temp_cards WHERE uid=%s", (uid,))
        r = cursor.fetchone()

        if r:
            cursor.execute("""
                INSERT INTO attendance (uid,name,grade,time,status,date)
                VALUES (%s,%s,%s,%s,%s,CURDATE())
            """, (uid, r['name'], r['grade'], time_now, "Temp"))

            db.commit()
            return "ACCESS_GRANTED"
        else:
            return "TEMP_NOT_FOUND"

    # 🟢 NORMAL CARD
    uid = uid_raw

    cursor.execute("SELECT * FROM students WHERE uid=%s", (uid,))
    r = cursor.fetchone()

    if not r:
        return "ACCESS_DENIED"

    cursor.execute("""
        INSERT INTO attendance (uid,name,grade,time,status,date)
        VALUES (%s,%s,%s,%s,%s,CURDATE())
    """, (uid, r['name'], r['grade'], time_now, "Present"))

    db.commit()

    return "ACCESS_GRANTED"


# 🔥 REQUIRED FOR RENDER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
