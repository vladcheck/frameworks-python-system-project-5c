from django.urls import path
from . import views

app_name = "concerts"

urlpatterns = [
    path("", views.concerts, name="concerts"),
    # Статический маршрут объявлен раньше динамического.
    path("statistics/", views.statistics, name="statistics"),
    path("create/", views.concert_create, name="concert_create"),
    path("<int:concert_id>/edit/", views.concert_update, name="concert_update"),
    path(
        "<int:concert_id>/cancel/",
        views.concert_cancel,
        name="concert_cancel",
    ),
    path("<int:concert_id>/", views.concert_detail, name="concert_detail"),
]
