# voice_assistant_wake.py
import speech_recognition as sr
import pyttsx3
import csv
import os
import datetime
import time

# ---------- Config ----------
WAKE_WORD = "hello"            # wake word you chose
DB_FILE = "appointments.csv"

# ---------- Setup ----------
r = sr.Recognizer()
engine = pyttsx3.init()

# tuning for faster response
r.energy_threshold = 300
r.dynamic_energy_threshold = True
r.pause_threshold = 0.5         # shorter pause detection
r.non_speaking_duration = 0.2

# ensure DB exists
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["vehicle_no", "appointment_time"])

# ---------- Helpers ----------
def speak(text):
    """Speak and print the text."""
    print("Bot:", text)
    engine.say(text)
    engine.runAndWait()   # blocks microphone while speaking, preventing overlap

def listen_short(timeout=2, phrase_time_limit=2):
    """
    Short listen used to detect wake word.
    Returns recognized text (lowercase) or "".
    """
    with sr.Microphone() as source:
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return ""
    try:
        text = r.recognize_google(audio, language="en-IN")
        print("You (short):", text)
        return text.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        # network / API issue
        print("STT request error")
        return ""

def listen_long(timeout=5, phrase_time_limit=5):
    """
    Longer listen for full user answers.
    Returns recognized text (lowercase) or "".
    """
    with sr.Microphone() as source:
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return ""
    try:
        text = r.recognize_google(audio, language="en-IN")
        print("You:", text)
        return text.lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        print("STT request error")
        return ""

# DB helpers
def load_db():
    records = {}
    with open(DB_FILE, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records[row["vehicle_no"].upper()] = row["appointment_time"]
    return records

def save_db(records):
    with open(DB_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["vehicle_no", "appointment_time"])
        for v, t in records.items():
            writer.writerow([v, t])

# small normalizations
def normalize_vehicle(text):
    return text.replace(" ", "").upper()

def greeting():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good morning!"
    elif hour < 18:
        return "Good afternoon!"
    else:
        return "Good evening!"

# ---------- Conversation steps ----------
def ask_vehicle_number():
    speak("Please tell me your vehicle number.")
    while True:
        # short listen then long if short returned something partial
        v = listen_long(timeout=5, phrase_time_limit=4)
        if v:
            vnorm = normalize_vehicle(v)
            speak(f"Did you say {vnorm}? Please say yes or no.")
            conf = listen_short(timeout=3, phrase_time_limit=2)
            if "yes" in conf or "correct" in conf:
                return vnorm
            else:
                speak("Okay, please say the vehicle number again.")
                continue
        else:
            speak("I did not hear the vehicle number. Please try again.")

def ask_appointment_time():
    speak("When can you bring your car for the wash? Please say date and time.")
    while True:
        t = listen_long(timeout=6, phrase_time_limit=6)
        if t:
            speak(f"Did you say {t}? Please say yes or no.")
            conf = listen_short(timeout=3, phrase_time_limit=2)
            if "yes" in conf or "correct" in conf:
                return t
            else:
                speak("Okay, please say the date and time again.")
        else:
            speak("I didn't hear that. Please say the date and time again.")

# ---------- Main assistant ----------
def run_assistant():
    speak(f"{greeting()} Welcome to Quick Car Wash. Say '{WAKE_WORD}' to start.")
    while True:
        # very short background listens waiting for wake word
        text = listen_short(timeout=3, phrase_time_limit=2)

        if text == "":
            continue

        # check for quit even in short-listen
        if "quit" in text or "exit" in text:
            speak("Goodbye! Have a nice day.")
            break

        # if wake word heard -> enter interaction mode
        if WAKE_WORD in text:
            # prevent listening while speaking by using speak() with blocking
            speak("Hello! How can I help you? You can say book, check or cancel an appointment.")
            # listen for user's intent
            intent = listen_short(timeout=4, phrase_time_limit=3)
            if intent == "":
                # try a more thorough listen
                intent = listen_long(timeout=6, phrase_time_limit=5)

            if intent == "":
                speak("I didn't catch that. Please say book, check or cancel.")
                continue

            if "book" in intent or "appointment" in intent or "book appointment" in intent:
                records = load_db()
                vehicle = ask_vehicle_number()
                if vehicle in records:
                    speak(f"Vehicle {vehicle} already has an appointment on {records[vehicle]}.")
                else:
                    timeslot = ask_appointment_time()
                    records[vehicle] = timeslot
                    save_db(records)
                    speak(f"Done. Your appointment for {vehicle} is booked for {timeslot}.")

            elif "check" in intent or "status" in intent:
                records = load_db()
                vehicle = ask_vehicle_number()
                if vehicle in records:
                    speak(f"Your appointment for {vehicle} is on {records[vehicle]}.")
                else:
                    speak("No appointment found for that vehicle.")

            elif "cancel" in intent or "remove" in intent:
                records = load_db()
                vehicle = ask_vehicle_number()
                if vehicle in records:
                    del records[vehicle]
                    save_db(records)
                    speak(f"Appointment for {vehicle} has been cancelled.")
                else:
                    speak("No appointment found to cancel.")

            elif "quit" in intent or "exit" in intent:
                speak("Goodbye! Have a nice day.")
                break

            else:
                speak("Sorry, I did not understand. Please say book, check or cancel.")

# ---------- run ----------
if __name__ == "__main__":
    run_assistant()
