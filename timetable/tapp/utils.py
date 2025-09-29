import random
from datetime import datetime, timedelta
from .models import Unit, Availability, AvailabilityBlock

# Define study blocks (fixed start times)
BLOCKS = {
    "morning": datetime.strptime("08:00", "%H:%M"),
    "afternoon": datetime.strptime("13:00", "%H:%M"),
    "evening": datetime.strptime("18:00", "%H:%M"),
}


def generate_timetable():
    """
    Generate a timetable directly from ORM objects (Unit + AvailabilityBlock).
    Returns a dict like:
    {
        "mon": [
            ("Math", 08:00, 10:00, "morning"),
            ("History", 13:00, 14:00, "afternoon")
        ],
        "tue": [...]
    }
    """

    units = Unit.objects.all()
    availabilities = Availability.objects.prefetch_related("blocks")

    if not units or not availabilities:
        return None  # Caller should handle error case

    # --- Normalize unit difficulties ---
    total_difficulty = sum(u.difficulty for u in units)
    total_hours = sum(
        sum(block.hours for block in a.blocks.all()) for a in availabilities
    )

    allocations = {
        u.name: max(1, int((u.difficulty / total_difficulty) * total_hours))
        for u in units
    }

    timetable = {a.day: [] for a in availabilities}

    # --- Assign units per day and per block ---
    for a in availabilities:
        for block in a.blocks.all():
            if block.hours <= 0:
                continue

            start_time = BLOCKS[block.block]
            daily_allocated = 0

            # Shuffle units for variety
            units_today = random.sample(list(allocations.keys()), len(allocations))

            for unit in units_today:
                if allocations[unit] <= 0 or daily_allocated >= block.hours:
                    continue

                # Allocate 1–2 hours at a time
                slot_hours = min(
                    random.randint(1, 2),
                    allocations[unit],
                    block.hours - daily_allocated,
                )

                end_time = start_time + timedelta(hours=slot_hours)

                timetable[a.day].append(
                    (unit, start_time.time(), end_time.time(), block.block)
                )

                allocations[unit] -= slot_hours
                daily_allocated += slot_hours
                start_time = end_time

    return timetable


def generate_reminders(timetable, reminder_offset=15):
    """
    Generate reminders for each study session.
    Reminder times are X minutes before session start.
    """
    reminders = []
    for day, sessions in timetable.items():
        for unit, start, _, block in sessions:
            now = datetime.now()
            session_start = now.replace(
                hour=start.hour, minute=start.minute, second=0, microsecond=0
            )
            reminder_time = session_start - timedelta(minutes=reminder_offset)

            reminders.append(
                {
                    "unit": unit,
                    "day": day,
                    "block": block,
                    "reminder_time": reminder_time,
                }
            )
    return reminders
