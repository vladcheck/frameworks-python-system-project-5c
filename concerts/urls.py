from django.urls import path
from . import views

app_name = "concerts"

urlpatterns = [
    path("", views.concerts, name="concerts"),
    path("<int:concert_id>/", views.concert_detail, name="concert_detail"),
]
