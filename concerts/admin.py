"""Регистрация модели концерта в административной панели."""

from django.contrib import admin

from .models import Concert


@admin.register(Concert)
class ConcertAdmin(admin.ModelAdmin):
    """Настройки списка концертов в административной панели."""

    list_display = (
        "id",
        "title",
        "date",
        "performer",
        "venue",
        "is_cancelled",
    )
    list_filter = ("is_cancelled", "date", "venue")
    search_fields = ("title", "performer__name", "venue__name")
    # Связанные объекты загружаются одним запросом.
    list_select_related = ("performer", "venue", "program")
