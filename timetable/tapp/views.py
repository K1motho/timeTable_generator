from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from .models import Unit, Availability, AvailabilitySlot, Timetable
from .utils import generate_timetable
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


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
        {"greeting": greeting, "day": day, "has_timetable": has_timetable},
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
        start_time_str = request.POST.get("start_time")
        end_time_str = request.POST.get("end_time")

        if day and start_time_str and end_time_str:
            try:
                start_time = datetime.strptime(start_time_str, "%H:%M").time()
                end_time = datetime.strptime(end_time_str, "%H:%M").time()

                if start_time >= end_time:
                    messages.error(request, "⚠️ End time must be later than start time.")
                else:
                    availability, _ = Availability.objects.get_or_create(day=day)
                    AvailabilitySlot.objects.create(
                        availability=availability,
                        start_time=start_time,
                        end_time=end_time,
                    )
                    messages.success(
                        request,
                        f"✅ Added availability for {availability.get_day_display()} {start_time}–{end_time}."
                    )
                    return redirect("availability_list")
            except ValueError:
                messages.error(request, "⚠️ Invalid time format. Please use HH:MM (24-hour).")
        else:
            messages.error(request, "⚠️ Please provide a valid day, start time, and end time.")

    availability = Availability.objects.prefetch_related("slots").all()
    return render(request, "availability_list.html", {"availability": availability})


def delete_availability_slot(request, slot_id):
    slot = get_object_or_404(AvailabilitySlot, id=slot_id)
    messages.success(
        request,
        f"🗑️ Removed availability slot for {slot.availability.get_day_display()} {slot.start_time}-{slot.end_time}."
    )
    slot.delete()
    return redirect("availability_list")


# ---------------------- Generate Timetable ----------------------
def generate(request):
    timetable_id = request.session.get("timetable_id")

    if timetable_id:
        timetable = Timetable.objects.filter(id=timetable_id).first()
        if timetable:
            messages.info(request, "ℹ️ Showing your previously generated timetable.")
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
    Handles user choice when they already have a timetable.
    option = cancel → Keep existing timetable
    option = new_only → Clear everything, go to fresh setup
    option = download_new → Download current timetable, then reset and go to fresh setup
    """
    timetable_id = request.session.get("timetable_id")
    timetable = Timetable.objects.filter(id=timetable_id).first() if timetable_id else None

    if option == "cancel":
        if timetable:
            messages.info(request, "ℹ️ Using your existing timetable.")
            return render(
                request,
                "result.html",
                {"timetable": timetable.data, "timetable_id": timetable.id},
            )
        messages.warning(request, "⚠️ No timetable to cancel. Redirecting home.")
        return redirect("home")

    if option == "download_new" and timetable:
        # Download old one first
        response = _build_pdf_response(timetable)
        # Clear data AFTER sending the PDF
        Unit.objects.all().delete()
        Availability.objects.all().delete()
        AvailabilitySlot.objects.all().delete()
        request.session.pop("timetable_id", None)
        return response

    if option == "new_only" or (option == "download_new" and not timetable):
        # Clear everything for fresh setup
        Unit.objects.all().delete()
        Availability.objects.all().delete()
        AvailabilitySlot.objects.all().delete()
        request.session.pop("timetable_id", None)

        messages.success(request, "🆕 Starting a fresh timetable setup.")
        return redirect("unit_list")


def finalize_generate(request):
    units = Unit.objects.all()
    availability = Availability.objects.prefetch_related("slots").all()

    if not units or not availability:
        messages.error(request, "⚠️ Please add both units and availability before generating.")
        return render(
            request,
            "error.html",
            {"message": "Please add units and availability first."},
        )

    timetable_data = generate_timetable()
    timetable = Timetable.objects.create(data=timetable_data)
    request.session["timetable_id"] = timetable.id

    messages.success(request, "✅ Timetable generated successfully!")
    return render(
        request,
        "result.html",
        {"timetable": timetable_data, "timetable_id": timetable.id},
    )


# ---------------------- Download Timetable ----------------------
def _build_pdf_response(timetable):
    """Helper to generate timetable PDF response."""
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="timetable.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, height - 50, "Your Timetable")

    p.setFont("Helvetica", 12)
    y = height - 100

    # Loop through sessions in timetable.data
    for day, sessions in timetable.data.items():
        p.setFont("Helvetica-Bold", 13)
        p.drawString(100, y, day)
        y -= 20

        p.setFont("Helvetica", 11)
        for session in sessions:
            text = f"{session['unit']} ({session['start']} - {session['end']})"
            p.drawString(120, y, text)
            y -= 15

            if y < 50:  # new page if space runs out
                p.showPage()
                y = height - 50

        y -= 10  # space between days

    p.showPage()
    p.save()
    return response


def download_timetable(request):
    timetable_id = request.session.get("timetable_id")
    timetable = Timetable.objects.filter(id=timetable_id).first()

    if not timetable:
        return HttpResponse("No timetable found.", status=404)

    return _build_pdf_response(timetable)
