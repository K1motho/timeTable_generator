from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    # --- Units ---
    path("units/", views.unit_list, name="unit_list"),
    path("units/delete/<int:unit_id>/", views.delete_unit, name="delete_unit"),

    # --- Availability ---
    path("availability/", views.availability_list, name="availability_list"),
    path("availability/delete/<int:slot_id>/", views.delete_availability_slot, name="delete_availability_slot"),

    # --- Timetable generation ---
    path("generate/", views.generate, name="generate"),
    path("generate/proceed/<str:option>/", views.proceed_generate, name="proceed_generate"),
    path("generate/finalize/", views.finalize_generate, name="finalize_generate"),

    #-- download timetable --
    path("download/", views.download_timetable, name="download_timetable"),

]
