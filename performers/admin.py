"""Регистрация модели исполнителя в административной панели."""

from django.contrib import admin

from concerts.models import Concert

from .models import Performer


class ConcertInline(admin.TabularInline):
    """Просмотр концертов исполнителя (внешние ключи защищены PROTECT)."""

    model = Concert
    fields = ("title", "venue", "program", "date", "status")
    readonly_fields = fields
    extra = 0
    can_delete = False


@admin.register(Performer)
class PerformerAdmin(admin.ModelAdmin):
    """Настройки списка исполнителей в административной панели."""

    list_display = ("id", "name", "genre", "rating")
    list_display_links = ("name",)
    list_filter = ("genre",)
    search_fields = ("name", "genre")
    ordering = ("name",)
    list_per_page = 20
    # Просмотр концертов исполнителя без возможности удаления (PROTECT).
    inlines = (ConcertInline,)
