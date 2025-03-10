from datetime import datetime, date, time, timedelta
import sqlite3

def setup_db():
    conn = sqlite3.connect('shifts.db')
    c = conn.cursor()

    # Create table for active shifts
    c.execute('''
    CREATE TABLE IF NOT EXISTS active_shifts (
        message_id TEXT PRIMARY KEY,
        channel_id TEXT,
        invoker_username TEXT,
        location TEXT,
        shift_date TEXT,
        time_from TEXT,
        time_to TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()

def generate_day_slots():
    day_slots = []
    current = date.today()

    end = current + timedelta(days=25)

    while current < end:
        day_slots.append(current)
        current += timedelta(days=1)

    return day_slots

def generate_time_slots(start_hour=8, end_hour=19, end_minutes=30):
    time_slots = []
    current = datetime.combine(datetime.min, time(hour=start_hour))
    end = datetime.combine(datetime.min, time(hour=end_hour, minute=end_minutes))

    while current <= end:
        time_slots.append(current.time())
        current += timedelta(minutes=30)

    return time_slots