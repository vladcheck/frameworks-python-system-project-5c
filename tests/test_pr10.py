"""Тесты практической работы №10: статусы, слаги, GeneratedField, контекст, админка."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from concerts.models import Concert
from performers.models import Performer
from programs.models import Program
from venues.models import Venue

client = Client()

FUTURE_DATE = date(2099, 3, 1)


@pytest.fixture
def pr10_factory():
    """Создавать объекты с уникальными id и удалять их после теста."""
    created = {"concerts": [], "programs": [], "venues": [], "performers": []}
    next_pk = {"value": 5001}

    def take_pk():
        pk = next_pk["value"]
        next_pk["value"] += 1
        return pk

    def make_performer(name="Исполнитель ПР10"):
        obj = Performer.objects.create(
            pk=take_pk(),
            name=name,
            genre="поп",
            rating=Decimal("8.0"),
        )
        created["performers"].append(obj.pk)
        return obj

    def make_venue(name="Площадка ПР10", capacity=1000):
        obj = Venue.objects.create(
            pk=take_pk(),
            name=name,
            city="Москва",
            capacity=capacity,
        )
        created["venues"].append(obj.pk)
        return obj

    def make_program(name="Программа ПР10"):
        obj = Program.objects.create(
            pk=take_pk(),
            name=name,
            duration=60,
            age_limit=12,
        )
        created["programs"].append(obj.pk)
        return obj

    def make_concert(
        venue=None,
        performer=None,
        program=None,
        title="Концерт ПР10",
        concert_date=FUTURE_DATE,
        status=Concert.Status.SCHEDULED,
    ):
        obj = Concert.objects.create(
            pk=take_pk(),
            title=title,
            performer=performer or Performer.objects.get(pk=1),
            venue=venue or Venue.objects.get(pk=1),
            program=program or Program.objects.get(pk=1),
            date=concert_date,
            expected_guests=100,
            base_ticket_price=Decimal("1000.00"),
            status=status,
        )
        created["concerts"].append(obj.pk)
        return obj

    yield SimpleNamespace(
        make_performer=make_performer,
        make_venue=make_venue,
        make_program=make_program,
        make_concert=make_concert,
    )

    Concert.objects.filter(pk__in=created["concerts"]).delete()
    Program.objects.filter(pk__in=created["programs"]).delete()
    Venue.objects.filter(pk__in=created["venues"]).delete()
    Performer.objects.filter(pk__in=created["performers"]).delete()


# --- Менеджер и QuerySet концертов по статусу ---


def test_manager_filters_by_status(pr10_factory):
    scheduled = pr10_factory.make_concert(status=Concert.Status.SCHEDULED)
    cancelled = pr10_factory.make_concert(status=Concert.Status.CANCELLED)
    completed = pr10_factory.make_concert(status=Concert.Status.COMPLETED)

    scheduled_pks = set(Concert.objects.scheduled().values_list("pk", flat=True))
    cancelled_pks = set(Concert.objects.cancelled().values_list("pk", flat=True))
    completed_pks = set(Concert.objects.completed().values_list("pk", flat=True))

    assert scheduled.pk in scheduled_pks
    assert cancelled.pk not in scheduled_pks
    assert cancelled.pk in cancelled_pks
    assert completed.pk in completed_pks
    assert scheduled.pk not in completed_pks


def test_manager_for_date(pr10_factory):
    concert = pr10_factory.make_concert(concert_date=FUTURE_DATE)
    other = pr10_factory.make_concert(
        concert_date=FUTURE_DATE.replace(day=2),
    )
    found = Concert.objects.for_date(FUTURE_DATE)
    assert concert.pk in set(found.values_list("pk", flat=True))
    assert other.pk not in set(found.values_list("pk", flat=True))


def test_manager_methods_chainable():
    chained = Concert.objects.scheduled().filter(title__icontains="Мейби")
    direct = Concert.objects.filter(
        title__icontains="Мейби",
        status=Concert.Status.SCHEDULED,
    )
    assert chained.count() == direct.count()


def test_cancel_sets_cancelled_status(pr10_factory):
    concert = pr10_factory.make_concert()
    concert.cancel()
    concert.refresh_from_db()
    assert concert.status == Concert.Status.CANCELLED


# --- Слаг площадки и get_absolute_url ---


def test_venue_slug_auto_generated(pr10_factory):
    venue = pr10_factory.make_venue(name="Новый Тестовый Зал")
    assert venue.slug == "новый-тестовый-зал"


def test_venue_slug_unique_for_same_name(pr10_factory):
    first = pr10_factory.make_venue(name="Одинаковое Название")
    second = pr10_factory.make_venue(name="Одинаковое Название")
    third = pr10_factory.make_venue(name="Одинаковое Название")
    assert first.slug == "одинаковое-название"
    assert second.slug == "одинаковое-название-2"
    assert third.slug == "одинаковое-название-3"


def test_venue_slug_not_regenerated_when_set(pr10_factory):
    venue = pr10_factory.make_venue(name="Кастомное имя")
    venue.name = "Другое имя"
    venue.save()
    assert venue.slug == "кастомное-имя"


def test_venue_seeded_slugs_match_names():
    venue = Venue.objects.get(pk=1)
    assert venue.slug == "adrenaline-stadium"


def test_venue_get_absolute_url(pr10_factory):
    venue = pr10_factory.make_venue(name="Зал Ссылка")
    assert venue.get_absolute_url() == reverse(
        "venues:venue_detail",
        kwargs={"slug": venue.slug},
    )


def test_venue_detail_by_slug_ok():
    response = client.get("/venues/adrenaline-stadium/")
    assert response.status_code == 200
    assert "Adrenaline Stadium" in response.content.decode()


def test_venue_detail_by_cyrillic_slug_ok():
    response = client.get("/venues/космонавт/")
    assert response.status_code == 200
    assert "Космонавт" in response.content.decode()


def test_venue_detail_unknown_slug_404():
    assert client.get("/venues/no-such-venue/").status_code == 404


def test_venue_list_links_use_slugs():
    content = client.get("/venues/").content.decode()
    assert 'href="/venues/adrenaline-stadium/"' in content


# --- GeneratedField is_large ---


def test_is_large_generated_on_create(pr10_factory):
    small = pr10_factory.make_venue(name="Малая площадка", capacity=499)
    large = pr10_factory.make_venue(name="Большая площадка", capacity=500)
    assert small.is_large is False
    assert large.is_large is True


def test_is_large_recomputed_on_save(pr10_factory):
    venue = pr10_factory.make_venue(name="Переменная площадка", capacity=100)
    venue.capacity = 1000
    venue.save()
    refreshed = Venue.objects.get(pk=venue.pk)
    assert refreshed.is_large is True


def test_is_large_stored_in_database(pr10_factory):
    venue = pr10_factory.make_venue(name="Площадка 500", capacity=500)
    refreshed = Venue.objects.get(pk=venue.pk)
    assert refreshed.is_large is True


# --- Контекстный процессор ---


def test_context_processor_adds_site_name():
    response = client.get("/concerts/")
    assert response.context["site_name"] == "Concerty"


def test_context_processor_adds_scheduled_concerts_count():
    response = client.get("/concerts/")
    expected = Concert.objects.scheduled().count()
    assert response.context["concerts_count"] == expected


def test_navigation_shows_concerts_count():
    content = client.get("/concerts/").content.decode()
    assert "Концерты (" in content


def test_base_template_uses_site_name_in_footer():
    content = client.get("/").content.decode()
    assert (
        '<footer class="container mt-4 mb-3">'
        "<p>© <span id=\"current-year\"></span> Concerty</p></footer>"
    ) in content


# --- Административная панель ---


@pytest.fixture
def admin_client():
    """Авторизованный клиент с временным суперпользователем."""
    user = User.objects.create_superuser(
        username="admin_pr10",
        email="admin_pr10@example.com",
        password="admin-password-123",
    )
    client.post(
        "/admin/login/",
        {"username": "admin_pr10", "password": "admin-password-123"},
    )
    try:
        yield client
    finally:
        client.logout()
        user.delete()


def test_admin_login_and_index(admin_client):
    response = admin_client.get("/admin/")
    assert response.status_code == 200
    assert "Администрирование сайта" in response.content.decode()


@pytest.mark.parametrize(
    "url",
    [
        "/admin/concerts/concert/",
        "/admin/venues/venue/",
        "/admin/performers/performer/",
        "/admin/programs/program/",
    ],
)
def test_admin_changelists_ok(admin_client, url):
    assert admin_client.get(url).status_code == 200


def test_admin_concert_changelist_search(admin_client):
    response = admin_client.get("/admin/concerts/concert/", {"q": "Мейби"})
    assert response.status_code == 200


def test_admin_concert_changelist_filters(admin_client):
    response = admin_client.get(
        "/admin/concerts/concert/",
        {"status__exact": Concert.Status.SCHEDULED},
    )
    assert response.status_code == 200
    response = admin_client.get("/admin/concerts/concert/", {"venue__id__exact": 1})
    assert response.status_code == 200


def test_admin_venue_changelist_filters(admin_client):
    response = admin_client.get(
        "/admin/venues/venue/",
        {"is_large__exact": "1"},
    )
    assert response.status_code == 200


def test_admin_venue_change_page_shows_concerts_inline(admin_client):
    response = admin_client.get("/admin/venues/venue/1/change/")
    assert response.status_code == 200
    content = response.content.decode()
    # Вложенный инлайн показывает концерты площадки без возможности удаления.
    assert "Клубный вечер с Мейби Бейби" in content


def test_admin_performer_change_page_shows_concerts_inline(admin_client):
    response = admin_client.get("/admin/performers/performer/1/change/")
    assert response.status_code == 200
    assert "Клубный вечер с Мейби Бейби" in response.content.decode()
