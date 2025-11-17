# app.py - Deewanshi Car Center Voice Assistant (Final Version)
from flask import Flask, render_template, request, jsonify
import os
import whisper
import pyttsx3
import sqlite3
from datetime import datetime, timedelta
import dateparser

app = Flask(__name__)

# ==================== CONFIG ====================
DB_FILE = "appointments.db"

# Load Whisper model
print("Loading Whisper model (base for speed)...")
model = whisper.load_model("base")
print("Model loaded!")

# ==================== DATABASE ====================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            vehicle_no TEXT NOT NULL UNIQUE,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ==================== TTS ====================
def speak(text):
    print(f"Assistant: {text}")
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        voices = engine.getProperty('voices')
        for v in voices:
            if any(x in v.name.lower() for x in ['zira', 'female', 'india']):
                engine.setProperty('voice', v.id)
                break
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except:
        pass

# ==================== VEHICLE NUMBER NORMALIZER ====================
def normalize_vehicle_no(text):
    """Convert any spoken vehicle number to clean format: PB123456"""
    cleaned = text.upper()
    cleaned = cleaned.replace(" ", "").replace("-", "").replace(".", "")
    # Remove common spoken words
    fillers = ["ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE", "TEN", "OH"]
    for f in fillers:
        cleaned = cleaned.replace(f, "")
    # Keep only letters and numbers
    cleaned = ''.join(c for c in cleaned if c.isalnum())
    return cleaned

# ==================== SESSION STATE ====================
class Session:
    def __init__(self):
        self.reset()
    def reset(self):
        self.stage = "welcome"
        self.user_name = None
        self.vehicle_no = None
        self.pref_date = None

session = Session()

# ==================== DB HELPERS ====================
def find_next_slot(date_str):
    base = dateparser.parse(date_str, settings={'PREFER_DATES_FROM': 'future'}) or datetime.now()
    check_date = base.date()
    slots = ["10:00", "13:00", "16:00"]

    for _ in range(30):
        d_str = check_date.strftime("%Y-%m-%d")
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT time FROM appointments WHERE date=?", (d_str,))
        booked = [r[0] for r in c.fetchall()]
        conn.close()

        for slot in slots:
            if slot not in booked:
                return d_str, slot
        check_date += timedelta(days=1)

    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    return tomorrow, "10:00"

def book_appointment(name, vehicle, date, time):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO appointments (username, vehicle_no, date, time) VALUES (?, ?, ?, ?)",
                  (name.title(), vehicle, date, time))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_appointment(vehicle):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, date, time FROM appointments WHERE vehicle_no=?", (vehicle,))
    result = c.fetchone()
    conn.close()
    return result

# ==================== ROUTES ====================
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start():
    session.reset()
    reply = "Good morning! Welcome to Deewanshi Car Center. May I know your name please?"
    speak(reply)
    session.stage = "ask_name"
    return jsonify({"reply": reply, "enable_mic": True})
@app.route('/listen', methods=['POST'])
def listen():
    user_input = request.json.get("message", "").strip().lower()
    reply = ""
    enable_mic = True
    done = False

    # Helper to speak + log
    def say(text):
        print(f"Assistant: {text}")
        speak(text)
        return text

    # ====================== CONFIRMATION STATES ======================
    if session.stage == "ask_name":
        session.user_name = user_input.title()
        reply = f"You said: {session.user_name}. Is this correct? Say yes or no."
        session.stage = "confirm_name"
        say(reply)

    elif session.stage == "confirm_name":
        if "yes" in user_input or "correct" in user_input:
            reply = "Okay, confirmed!"
            say(reply)
            reply = f"Thank you {session.user_name.split()[0]}! How can I help you today? Say 'book appointment' or 'car status'."
            session.stage = "main_menu"
        else:
            reply = "Sorry, please say your name again."
            session.stage = "ask_name"
        say(reply)

    elif session.stage == "main_menu":
        if any(x in user_input for x in ["book", "appointment", "service"]):
            reply = "Please tell me your vehicle number."
            session.stage = "get_vehicle"
        elif any(x in user_input for x in ["status", "check", "ready"]):
            reply = "Please say your vehicle number to check status."
            session.stage = "check_status"
        else:
            reply = "Please say 'book appointment' or 'car status'."
        say(reply)

    elif session.stage == "get_vehicle":
        session.vehicle_no = normalize_vehicle_no(user_input)
        if len(session.vehicle_no) < 6:
            reply = "That doesn't sound right. Please say your vehicle number again."
            session.stage = "get_vehicle"
        else:
            reply = f"You said: {session.vehicle_no}. Is this correct? Say yes or no."
            session.stage = "confirm_vehicle"
        say(reply)

    elif session.stage == "confirm_vehicle":
        if "yes" in user_input or "correct" in user_input:
            reply = "Okay, confirmed!"
            say(reply)
            reply = "What date would you like? For example, tomorrow, 20 November, or next week."
            session.stage = "get_date"
        else:
            reply = "Please say your vehicle number again."
            session.stage = "get_vehicle"
        say(reply)

    elif session.stage == "get_date":
        session.pref_date = user_input
        reply = f"You said: {user_input.title()}. Is this correct? Say yes or no."
        session.stage = "confirm_date"
        say(reply)

    elif session.stage == "confirm_date":
        if "yes" in user_input or "correct" in user_input:
            reply = "Okay, confirmed!"
            say(reply)
            reply = "What time would you prefer? Like 10 AM, 2 PM, or 4 PM?"
            session.stage = "get_time"
        else:
            reply = "Please say the date again."
            session.stage = "get_date"
        say(reply)

    elif session.stage == "get_time":
        session.pref_time = user_input
        reply = f"You said: {user_input.title()}. Is this correct? Say yes or no."
        session.stage = "confirm_time"
        say(reply)

    elif session.stage == "confirm_time":
        if "yes" in user_input or "correct" in user_input:
            reply = "Okay, confirmed!"
            say(reply)
            date_slot, time_slot = find_next_slot(session.pref_date)
            success = book_appointment(session.user_name, session.vehicle_no, date_slot, time_slot)
            nice_date = datetime.strptime(date_slot, "%Y-%m-%d").strftime("%d %B %Y")

            if success:
                reply = f"Excellent! Your appointment is booked for {nice_date} at {time_slot}."
                say(reply)
                reply = f"We will take good care of your car {session.vehicle_no}. Thank you!"
            else:
                reply = f"Sorry, {session.vehicle_no} already has an appointment."
            say(reply)
            reply = "Do you need any other help?"
            session.stage = "final_ask"
        else:
            reply = "Please say the time again."
            session.stage = "get_time"
        say(reply)

    elif session.stage == "final_ask":
        if "no" in user_input or "thank" in user_input:
            reply = f"Thank you {session.user_name.split()[0]}! Have a wonderful day!"
            say(reply)
            session.reset()
            done = True
        else:
            reply = "How else may I assist you?"
            session.stage = "main_menu"
        say(reply)

    # ====================== STATUS CHECK ======================
    elif session.stage == "check_status":
        vehicle = normalize_vehicle_no(user_input)
        appt = get_appointment(vehicle)
        if appt:
            name, date, time = appt
            nice_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d %B %Y")
            reply = f"Hello {name.split()[0]}! Your car {vehicle} will be ready on {nice_date} at {time}."
        else:
            reply = "No appointment found for this vehicle number."
        say(reply)
        session.reset()
        done = True

    return jsonify({
        "reply": reply,
        "enable_mic": enable_mic,
        "done": done
    })# ==================== ADMIN DATABASE ROUTE (Password protected in frontend) ====================
@app.route('/admin/database')
def admin_database():
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, username, vehicle_no, date, time FROM appointments ORDER BY date ASC, time ASC")
        rows = c.fetchall()
        conn.close()

        appointments = []
        for row in rows:
            appointments.append({
                "id": row[0],
                "username": row[1],
                "vehicle_no": row[2],
                "date": row[3],
                "time": row[4]
            })
        
        return jsonify(appointments)
    
    except Exception as e:
        print(f"Admin database error: {e}")
        return jsonify([]), 500

# ==================== RUN ====================
if __name__ == '__main__':
    print("\n" + "="*60)
    print("   DEEWANSHI CAR CENTER VOICE ASSISTANT IS READY!")
    print("   Open your browser → http://127.0.0.1:5000")
    print("="*60 + "\n")
    app.run(debug=False, port=5000)