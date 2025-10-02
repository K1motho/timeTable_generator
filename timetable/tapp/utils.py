import random
from datetime import datetime, timedelta
from .models import Unit, Availability, AvailabilitySlot


def generate_timetable():
    """
    Generate a timetable from Unit + AvailabilitySlot.
    Returns a dict like:
    {
        "mon": [
            {"unit": "Math", "start": "10:00", "end": "11:30"},
            {"unit": "History", "start": "16:00", "end": "17:00"}
        ],
        "tue": [...]
    }
    """

    units = Unit.objects.all()
    availabilities = Availability.objects.prefetch_related("slots")

    if not units or not availabilities:
        return None

    # --- Normalize difficulty weights ---
    total_difficulty = sum(u.difficulty for u in units)
    if total_difficulty == 0:
        return None

    # --- Count total available hours ---
    total_hours = 0
    slots_by_day = {}
    for a in availabilities:
        slots_by_day[a.day] = []
        for slot in a.slots.all():
            if slot.start_time and slot.end_time:
                diff = (
                    datetime.combine(datetime.today(), slot.end_time)
                    - datetime.combine(datetime.today(), slot.start_time)
                ).seconds // 3600
                if diff > 0:
                    total_hours += diff
                    slots_by_day[a.day].append(
                        {
                            "start": slot.start_time,
                            "end": slot.end_time,
                            "hours": diff,
                        }
                    )

    if total_hours == 0:
        return None

    # --- Allocate weekly hours per unit (respect difficulty) ---
    allocations = {
        u.name: max(1, int((u.difficulty / total_difficulty) * total_hours))
        for u in units
    }

    # --- Timetable structure ---
    timetable = {day: [] for day in slots_by_day.keys()}

    # --- Assign sessions into slots ---
    # We iterate day by day, slot by slot, and fill units
    for day, slots in slots_by_day.items():
        for slot in slots:
            start_time = datetime.combine(datetime.today(), slot["start"])
            end_time = datetime.combine(datetime.today(), slot["end"])
            available_hours = slot["hours"]

            # While slot has hours and there are units needing time
            while available_hours > 0 and any(v > 0 for v in allocations.values()):
                # Pick a unit that still has hours left
                # Sort by remaining hours (so harder units get priority)
                unit = max(allocations, key=lambda k: allocations[k])

                if allocations[unit] <= 0:
                    break

                # Allocate the smaller of remaining hours and slot capacity
                slot_hours = min(allocations[unit], available_hours)

                unit_end = start_time + timedelta(hours=slot_hours)

                timetable[day].append(
                    {
                        "unit": unit,
                        "start": start_time.strftime("%H:%M"),
                        "end": unit_end.strftime("%H:%M"),
                    }
                )

                # Deduct
                allocations[unit] -= slot_hours
                available_hours -= slot_hours
                start_time = unit_end

    return timetable


def generate_reminders(timetable, reminder_offset=15):
    """
    Generate reminders for each study session.
    Reminder times are X minutes before session start.
    """
    reminders = []
    for day, sessions in timetable.items():
        for session in sessions:
            unit = session["unit"]
            start = session["start"]  # "HH:MM"

            # Convert back into datetime for reminder
            now = datetime.now()
            session_start = now.replace(
                hour=int(start.split(":")[0]),
                minute=int(start.split(":")[1]),
                second=0,
                microsecond=0,
            )
            reminder_time = session_start - timedelta(minutes=reminder_offset)

            reminders.append(
                {
                    "unit": unit,
                    "day": day,
                    "reminder_time": reminder_time.strftime("%Y-%m-%d %H:%M"),
                }
            )
    return reminders
