"""Общие фикстуры pytest: Django, временная БД и тестовые данные.

Тесты никогда не обращаются к рабочей базе db.sqlite3: на время сессии
создаётся отдельный временный файл SQLite, в который применяются миграции
и загружаются данные из data/*.json с сохранением исходных идентификаторов.
"""

import os
from decimal import Decimal
from pathlib import Path

import django
import pytest
from django.test.utils import setup_test_environment, teardown_test_environment

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "concerty.settings")
django.setup()

from django.conf import settings  # noqa: E402
from django.core.management import call_command  # noqa: E402
from django.db import connections  # noqa: E402

from concerts.models import Concert  # noqa: E402
from performers.models import Performer  # noqa: E402
from programs.models import Program  # noqa: E402
from src.storage import (  # noqa: E402
    load_concerts,
    load_performers,
    load_programs,
    load_venues,
)
from venues.models import Venue  # noqa: E402

BASE_DIR = Path(settings.BASE_DIR)
DATA_DIR = BASE_DIR / "data"

# Количество записей в data/*.json, которое должно попасть в тестовую БД.
EXPECTED_COUNTS = {
    "performers": 12,
    "venues": 12,
    "programs": 12,
    "concerts": 15,
}


def _seed_database() -> None:
    """Заполнить тестовую БД через ORM, сохранив идентификаторы из JSON."""
    performers = load_performers(str(DATA_DIR / "performers.json"))
    venues = load_venues(str(DATA_DIR / "venues.json"))
    programs = load_programs(str(DATA_DIR / "programs.json"))
    concerts = load_concerts(
        str(DATA_DIR / "concerts.json"),
        performers,
        venues,
        programs,
    )

    Performer.objects.bulk_create(
        [
            Performer(
                pk=item.id,
                name=item.name,
                genre=item.genre,
                rating=Decimal(str(item.rating)),
            )
            for item in performers
        ]
    )
    Venue.objects.bulk_create(
        [
            Venue(
                pk=item.id,
                name=item.name,
                city=item.city,
                capacity=item.capacity,
            )
            for item in venues
        ]
    )
    Program.objects.bulk_create(
        [
            Program(
                pk=item.id,
                name=item.name,
                duration=item.duration,
                age_limit=item.age_limit,
            )
            for item in programs
        ]
    )
    Concert.objects.bulk_create(
        [
            Concert(
                pk=item.id,
                title=item.title,
                performer_id=item.performer.id,
                venue_id=item.venue.id,
                program_id=item.program.id,
                date=item.date,
                expected_guests=item.expected_guests,
                base_ticket_price=Decimal(str(item.base_ticket_price)),
                is_cancelled=item.is_cancelled,
            )
            for item in concerts
        ]
    )

    assert Performer.objects.count() == EXPECTED_COUNTS["performers"]
    assert Venue.objects.count() == EXPECTED_COUNTS["venues"]
    assert Program.objects.count() == EXPECTED_COUNTS["programs"]
    assert Concert.objects.count() == EXPECTED_COUNTS["concerts"]


@pytest.fixture(scope="session", autouse=True)
def django_test_database(tmp_path_factory):
    """Подготовить временную БД Django и загрузить в неё тестовые данные."""
    # Закрываем возможные соединения до подмены пути к базе.
    connections.close_all()

    db_path = tmp_path_factory.mktemp("django-db") / "test.sqlite3"
    settings.DATABASES["default"]["NAME"] = str(db_path)
    real_db = (BASE_DIR / "db.sqlite3").resolve()
    assert Path(settings.DATABASES["default"]["NAME"]).resolve() != real_db

    if "testserver" not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, "testserver"]

    setup_test_environment()
    try:
        call_command("migrate", verbosity=0, interactive=False)
        _seed_database()
        yield
    finally:
        connections.close_all()
        teardown_test_environment()
