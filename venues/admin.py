"""Регистрация модели площадки в административной панели."""

from django.contrib import admin

from concerts.models import Concert

from .models import Venue


class ConcertInline(admin.TabularInline):
    """Просмотр концертов площадки (внешние ключи защищены PROTECT)."""

    model = Concert
    fields = ("title", "performer", "program", "date", "status")
    readonly_fields = fields
    extra = 0
    can_delete = False


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    """Настройки списка площадок в административной панели."""

    list_display = ("id", "name", "city", "capacity", "slug", "is_large")
    list_display_links = ("name",)
    list_filter = ("city", "is_large")
    search_fields = ("name", "city")
    ordering = ("name",)
    list_per_page = 20
    # Просмотр концертов площадки без возможности удаления (PROTECT).
    inlines = (ConcertInline,)
