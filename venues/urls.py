from django.urls import path
from . import views

app_name = "venues"

urlpatterns = [
    path("", views.venues, name="venues"),
    # Статический маршрут объявлен раньше динамического.
    path("available/", views.available_venues, name="available"),
    path("<int:venue_id>/", views.venue_detail, name="venue_detail"),
]
