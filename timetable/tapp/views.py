from django.shortcuts import render, redirect
from .models import Unit, Availability
from .utils import generate_timetable

def home(request):
    return render(request, "timetable/home.html")

def unit_list(request):
    if request.method == "POST":
        name = request.POST.get("name")
        difficulty = int(request.POST.get("difficulty"))
        if name and 1 <= difficulty <=10:
            Unit.objects.create(name=name, difficulty=difficulty)
            return redirect("unit_list")
        
    units= Unit.objects.all()
    return render(request, "timetable/unit_list.html", {"units": units})
        
def availability_list(request):
    if request.method == "POST":
        day = request.POST.get('day')
        hours = int(request.POST.get("day"))
        if day and hours > 0 :
            Availability.objects.update_or_create(
                day=day, defaults={"hours_available": hours}
            )
            return redirect("availability_list")
        availability = Availability.objects.all()
        return render (
            request, "timetable/availability_list.html", {"availability": availability}
        )
def generate(request):
    units = Unit.objects.all()
    availability = Availability.objects.all()
        
    if not units or not availability:
        return render (request,
                      "timetable/error.html",
                      {"message": "Please add units and availability first."},
                       )
    timetable= generate_timetable(units, availability)
    return render(request, "timetable/result.html", {"timetable": timetable} )