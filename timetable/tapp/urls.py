from django.urls import path
from . import views 

urlpatterns = [
    path("", views.home, name="home" ),
    path("units/", views.unit_list, name="unit_list"),
    path("availability/", views.availability_list, name="availability_list"),
    path("generate/", views.generate, name="generate")
]
