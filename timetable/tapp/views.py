from django.shortcuts import render, redirect
from .models import Unit, Availability, AvailabilityBlock
from .utils import generate_timetable
from .models import Timetable
from datetime import datetime



def home(request):
    # Greeting message
    now = datetime.now()
    hour = now.hour
    if hour < 12:
        greeting = "morning"
    elif hour < 18:
        greeting = "afternoon"
    else:
        greeting = "evening"

    day = now.strftime("%A")

    # Check if timetable exists in session
    has_timetable = "timetable" in request.session

    return render(
        request,
        "home.html",
        {
            "greeting": greeting,
            "day": day,
            "has_timetable": has_timetable,
        },
    )

# ---------------------- Units ----------------------
def unit_list(request):
    if request.method == "POST":
        name = request.POST.get("name")
        difficulty = int(request.POST.get("difficulty", 5))
        if name and 1 <= difficulty <= 10:
            Unit.objects.create(name=name, difficulty=difficulty)
            return redirect("unit_list")

    units = Unit.objects.all()
    return render(request, "unit_list.html", {"units": units})


# ---------------------- Availability ----------------------
def availability_list(request):
    if request.method == "POST":
        day = request.POST.get("day")
        block = request.POST.get("block")
        hours = int(request.POST.get("hours", 0))

        if day and block and hours > 0:
            # Get or create the Availability for that day
            availability, _ = Availability.objects.get_or_create(day=day)
            # Update or create the block under that day
            AvailabilityBlock.objects.update_or_create(
                availability=availability,
                block=block,
                defaults={"hours": hours},
            )
            return redirect("availability_list")

    availability = Availability.objects.prefetch_related("blocks").all()
    return render(
        request,
        "availability_list.html",
        {"availability": availability},
    )


# ---------------------- Generate Timetable ----------------------
def generate(request):
    units = Unit.objects.all()
    availability = Availability.objects.all()

    if not units or not availability:
        return render(
            request,
            "timetable/error.html",
            {"message": "Please add units and availability first."},
        )

    # Generate timetable
    timetable = generate_timetable(units, availability)

    # Save in PostgreSQL
    t = Timetable.objects.create(data=timetable)

    return render(request, "result.html", {"timetable": timetable, "timetable_id": t.id})