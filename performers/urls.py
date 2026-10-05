from django.urls import path
from . import views

urlpatterns = [
    path("", views.performers, name="performers"),
    path(
        "<int:performer_id>/",
        views.performer_detail,
        name="performer_detail",
    ),
]
