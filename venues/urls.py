from django.urls import path, register_converter
from . import views


class UnicodeSlugConverter:
    """Конвертер слага: как стандартный slug, но с поддержкой кириллицы."""

    regex = r"[-\w]+"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


# Стандартный конвертер slug не пропускает кириллические слаги площадок,
# поэтому зарегистрирован отдельный конвертер uslug.
register_converter(UnicodeSlugConverter, "uslug")

app_name = "venues"

urlpatterns = [
    path("", views.venues, name="venues"),
    # Статический маршрут объявлен раньше динамического.
    path("available/", views.available_venues, name="available"),
    path("<uslug:slug>/", views.venue_detail, name="venue_detail"),
]
