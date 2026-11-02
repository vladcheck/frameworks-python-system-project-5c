from django.urls import path

from . import views

app_name = "homepage"

urlpatterns = [
    path("", views.index, name="index"),
    path("demo-escape/", views.demo_escape, name="demo_escape"),
]
