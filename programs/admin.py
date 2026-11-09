"""Регистрация модели программы в административной панели."""

from django.contrib import admin

from concerts.models import Concert

from .models import Program


class ConcertInline(admin.TabularInline):
    """Просмотр концертов с этой программой (FK защищены PROTECT)."""

    model = Concert
    fields = ("title", "performer", "venue", "date", "status")
    readonly_fields = fields
    extra = 0
    can_delete = False


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    """Настройки списка программ в административной панели."""

    list_display = ("id", "name", "duration", "age_limit")
    list_display_links = ("name",)
    list_filter = ("age_limit",)
    search_fields = ("name",)
    ordering = ("name",)
    list_per_page = 20
    # Просмотр концертов программы без возможности удаления (PROTECT).
    inlines = (ConcertInline,)
