from django.urls import path
from . import views

app_name = "programs"

urlpatterns = [
    path("", views.programs, name="programs"),
    path("<int:program_id>/", views.program_detail, name="program_detail"),
]
