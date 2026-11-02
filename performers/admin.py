"""Регистрация модели исполнителя в административной панели."""

from django.contrib import admin

from .models import Performer


@admin.register(Performer)
class PerformerAdmin(admin.ModelAdmin):
    """Настройки списка исполнителей в административной панели."""

    list_display = ("id", "name", "genre", "rating")
    list_filter = ("genre",)
    search_fields = ("name", "genre")
