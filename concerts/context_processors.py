"""Контекстные процессоры приложения concerts."""

from django.http import HttpRequest

from .models import Concert


def concert_context(request: HttpRequest) -> dict:
    """Добавить в контекст каждой страницы имя сайта и число концертов."""
    return {
        "site_name": "Concerty",
        "concerts_count": Concert.objects.scheduled().count(),
    }
