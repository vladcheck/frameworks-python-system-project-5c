"""Регистрация модели площадки в административной панели."""

from django.contrib import admin

from .models import Venue


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    """Настройки списка площадок в административной панели."""

    list_display = ("id", "name", "city", "capacity")
    list_filter = ("city",)
    search_fields = ("name", "city")
