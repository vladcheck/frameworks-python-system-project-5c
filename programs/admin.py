"""Регистрация модели программы в административной панели."""

from django.contrib import admin

from .models import Program


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    """Настройки списка программ в административной панели."""

    list_display = ("id", "name", "duration", "age_limit")
    list_filter = ("age_limit",)
    search_fields = ("name",)
