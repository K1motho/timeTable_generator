import random
from datetime import datetime, timedelta

# Define study blocks (fixed start times)
BLOCKS = {
    "morning": datetime.strptime("08:00", "%H:%M"),
    "afternoon": datetime.strptime("13:00", "%H:%M"),
    "evening": datetime.strptime("18:00", "%H:%M"),
}

def generate_timetable(units, availability):
    # normalize difficulties
    total_difficulty = sum(u['difficulty'] for u in units)
    total_hours = sum(sum(block.values()) for block in availability.values())
    allocations = {
        u["name"]: max(1, int((u["difficulty"] / total_difficulty) * total_hours))
        for u in units
    }

    timetable = {day: [] for day in availability.keys()}

    # assign units per day and per block
    for day, blocks in availability.items():
        for block_name, hours in blocks.items():
            if hours <= 0:
                continue

            start_time = BLOCKS[block_name]
            daily_allocated = 0

            # shuffle for variety
            units_today = random.sample(list(allocations.keys()), len(allocations))

            for unit in units_today:
                if allocations[unit] <= 0 or daily_allocated >= hours:
                    continue

                slot_hours = min(random.randint(1, 2), allocations[unit], hours - daily_allocated)
                end_time = start_time + timedelta(hours=slot_hours)

                timetable[day].append((unit, start_time.time(), end_time.time(), block_name))

                allocations[unit] -= slot_hours
                daily_allocated += slot_hours
                start_time = end_time

    return timetable


def generate_reminders(timetable, reminder_offset=15):
    reminders = []
    for day, sessions in timetable.items():
        for unit, start, _, block in sessions:
            now = datetime.now()
            session_start = now.replace(hour=start.hour, minute=start.minute, second=0, microsecond=0)
            reminder_time = session_start - timedelta(minutes=reminder_offset)

            reminders.append({
                "unit": unit,
                "day": day,
                "block": block,
                "reminder_time": reminder_time,
            })
    return reminders
