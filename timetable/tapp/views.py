from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Unit, Availability, AvailabilityBlock, Timetable
from .utils import generate_timetable
from datetime import datetime


# ---------------------- Home ----------------------
def home(request):
    now = datetime.now()
    hour = now.hour
    if hour < 12:
        greeting = "morning"
    elif hour < 18:
        greeting = "afternoon"
    else:
        greeting = "evening"

    day = now.strftime("%A")

    has_timetable = "timetable_id" in request.session

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
            messages.success(request, f"✅ Unit '{name}' added successfully!")
            return redirect("unit_list")
        else:
            messages.error(request, "⚠️ Invalid unit details. Please try again.")

    units = Unit.objects.all()
    return render(request, "unit_list.html", {"units": units})


def delete_unit(request, unit_id):
    unit = get_object_or_404(Unit, id=unit_id)
    unit.delete()
    messages.success(request, f"🗑️ Unit '{unit.name}' deleted successfully.")
    return redirect("unit_list")


# ---------------------- Availability ----------------------
def availability_list(request):
    if request.method == "POST":
        day = request.POST.get("day")
        block = request.POST.get("block")
        hours = int(request.POST.get("hours", 0))

        if day and block and hours > 0:
            availability, _ = Availability.objects.get_or_create(day=day)
            AvailabilityBlock.objects.update_or_create(
                availability=availability,
                block=block,
                defaults={"hours": hours},
            )
            messages.success(request, f"✅ Availability updated for {day.capitalize()} - {block}.")
            return redirect("availability_list")
        else:
            messages.error(request, "⚠️ Please select a valid day, block, and enter hours > 0.")

    availability = Availability.objects.prefetch_related("blocks").all()
    return render(
        request,
        "availability_list.html",
        {"availability": availability},
    )


# ---------------------- Generate Timetable ----------------------
def generate(request):
    """
    Handle initial Generate button click.
    If timetable exists → render it.
    If not → redirect to units page to start new.
    """
    timetable_id = request.session.get("timetable_id")

    if timetable_id:
        timetable = Timetable.objects.filter(id=timetable_id).first()
        if timetable:
            messages.info(request, " Showing your previously generated timetable.")
            return render(
                request,
                "result.html",
                {"timetable": timetable.data, "timetable_id": timetable.id},
            )
        else:
            messages.warning(request, "⚠️ No timetable found in session. Please create a new one.")

    return redirect("unit_list")


def proceed_generate(request, option):
    """
    option = "download_new" | "new_only" | "cancel"
    Triggered after toast decision.
    """
    timetable_id = request.session.get("timetable_id")
    timetable = Timetable.objects.filter(id=timetable_id).first() if timetable_id else None

    if option == "cancel":
        if timetable:
            messages.info(request, "ℹ️ Using your existing timetable.")
            return render(request, "result.html", {"timetable": timetable.data, "timetable_id": timetable.id})
        messages.warning(request, "⚠️ No timetable to cancel. Redirecting home.")
        return redirect("home")

    if option in ["download_new", "new_only"]:
        # Clear old timetable data
        Unit.objects.all().delete()
        Availability.objects.all().delete()
        AvailabilityBlock.objects.all().delete()
        request.session.pop("timetable_id", None)

        messages.success(request, "🆕 Starting a fresh timetable setup.")
        return redirect("unit_list")


def finalize_generate(request):
    """
    Generates timetable once Units + Availability are provided.
    """
    units = Unit.objects.all()
    availability = Availability.objects.all()

    if not units or not availability:
        messages.error(request, "⚠️ Please add both units and availability before generating.")
        return render(
            request,
            "error.html",
            {"message": "Please add units and availability first."},
        )

    timetable_data = generate_timetable(units, availability)
    timetable = Timetable.objects.create(data=timetable_data)
    request.session["timetable_id"] = timetable.id

    messages.success(request, "🎉 Timetable generated successfully!")
    return render(
        request,
        "result.html",
        {"timetable": timetable_data, "timetable_id": timetable.id},
    )
