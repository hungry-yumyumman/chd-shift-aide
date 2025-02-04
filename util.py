from datetime import datetime, date, time, timedelta

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