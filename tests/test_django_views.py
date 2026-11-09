"""Тесты Django-представлений через test Client на тестовой БД."""

import re
from datetime import date
from decimal import Decimal

import pytest
from django.test import Client, override_settings

from concerts.models import Concert

client = Client()

LIST_PAGES = [
    "/concerts/",
    "/venues/",
    "/performers/",
    "/programs/",
]

DETAIL_PAGES = [
    ("/concerts/1/", "Клубный вечер с Мейби Бейби"),
    ("/venues/adrenaline-stadium/", "Adrenaline Stadium"),
    ("/performers/1/", "Мейби Бейби"),
    ("/programs/1/", "MAYDAY: клубный сет"),
]

MISSING_PAGES = [
    "/concerts/999/",
    "/venues/no-such-venue/",
    "/performers/999/",
    "/programs/999/",
]


def _content(response) -> str:
    """Вернуть HTML-код ответа строкой."""
    return response.content.decode()


def _concert_titles(response) -> list[str]:
    """Извлечь названия концертов из карточек списка."""
    return re.findall(
        r'<h5 class="card-title">([^<]+)</h5>',
        _content(response),
    )


@pytest.fixture
def cancelled_concert():
    """Временно отменить концерт 1, чтобы проверить отменённые концерты."""
    concert = Concert.objects.get(pk=1)
    concert.cancel()
    try:
        yield concert
    finally:
        Concert.objects.filter(pk=1).update(status=Concert.Status.COMPLETED)


@pytest.fixture
def venue1_future_concert():
    """Создать запланированный концерт на площадке 1 в далёком будущем."""
    concert = Concert.objects.create(
        title="Будущий тестовый концерт",
        performer_id=1,
        venue_id=1,
        program_id=1,
        date=date(2099, 3, 1),
        expected_guests=100,
        base_ticket_price=Decimal("1000.00"),
    )
    try:
        yield concert
    finally:
        concert.delete()


# --- Базовые страницы (сохранены из исходного набора тестов) ---


def test_index_ok():
    response = client.get("/")
    assert response.status_code == 200
    content = _content(response)
    for url in LIST_PAGES:
        assert f'href="{url}"' in content


def test_list_pages_ok():
    for url in LIST_PAGES:
        response = client.get(url)
        assert response.status_code == 200
        content = _content(response)
        assert "<!DOCTYPE html>" in content
        assert 'href="/"' in content


def test_detail_pages_ok():
    for url, title in DETAIL_PAGES:
        response = client.get(url)
        assert response.status_code == 200
        assert title in _content(response)


def test_detail_back_links():
    pairs = [
        ("/concerts/1/", "/concerts/"),
        ("/venues/adrenaline-stadium/", "/venues/"),
        ("/performers/1/", "/performers/"),
        ("/programs/1/", "/programs/"),
    ]
    for detail_url, list_url in pairs:
        content = _content(client.get(detail_url))
        assert list_url in content


def test_missing_details_404():
    for url in MISSING_PAGES:
        assert client.get(url).status_code == 404


@override_settings(DEBUG=False)
def test_custom_404_page():
    response = client.get("/nonexistent/")
    assert response.status_code == 404
    content = _content(response)
    assert "страница не найдена" in content
    assert "404" in content


# --- Список концертов: данные, пагинация, фильтры, сортировка ---


def test_concerts_list_default_order_and_pagination():
    response = client.get("/concerts/")
    assert response.status_code == 200
    assert response.context["total_count"] == 159
    assert response.context["page_obj"].number == 1
    assert response.context["page_obj"].paginator.num_pages == 27
    # По умолчанию сортировка по дате, затем по pk.
    assert _concert_titles(response) == [
        "Свидание в Космонавте",
        "Мукка: соло-концерт",
        "Звери: акустика",
        "Буерак: пост-панк ночь",
        "Пошлая Молли: панк-вечеринка",
        "Дайте танк (!): нео-панк шоу",
    ]


def test_concerts_pagination_second_page():
    first = _content(client.get("/concerts/"))
    second = client.get("/concerts/?page=2")
    assert second.status_code == 200
    assert second.context["page_obj"].number == 2
    assert len(second.context["page_obj"].object_list) == 6
    assert "Клубный вечер с Мейби Бейби" not in first
    assert "Клубный вечер с Мейби Бейби" in _content(second)
    assert _concert_titles(second) == [
        "Клубный вечер с Мейби Бейби",
        "Аигел: трип-хоп сессия",
        "Дора: вечер инди",
        "Мейби Бейби в Питере",
        "Буерак: концерт 01.11",
        "Мот: концерт 01.11",
    ]


def test_concerts_pagination_third_page():
    third = client.get("/concerts/?page=3")
    assert third.status_code == 200
    assert third.context["page_obj"].number == 3
    assert _concert_titles(third) == [
        "Звери: концерт 01.11",
        "Мумий Тролль: концерт 01.11",
        "Пошлая Молли: концерт 02.11",
        "Мот: концерт 02.11",
        "ЛСП: концерт 02.11",
        "Мукка: концерт 02.11",
    ]


def test_concerts_invalid_page_returns_first_page():
    response = client.get("/concerts/?page=abc")
    assert response.status_code == 200
    assert response.context["page_obj"].number == 1
    assert len(response.context["page_obj"].object_list) == 6


def test_concerts_pagination_keeps_filters():
    response = client.get("/concerts/?status=active&sort=title")
    assert response.status_code == 200
    content = _content(response)
    assert re.search(
        r'href="[^"]*status=active[^"]*page=2[^"]*"',
        content,
    )


@pytest.mark.parametrize(
    ("query", "expected_count", "page_titles"),
    [
        (
            "Мейби",
            9,
            [
                "Клубный вечер с Мейби Бейби",
                "Мейби Бейби в Питере",
                "Мейби Бейби: концерт 08.11",
                "Мейби Бейби: концерт 09.11",
                "Мейби Бейби: концерт 11.11",
                "Мейби Бейби: концерт 26.11",
            ],
        ),
        (
            "Аигел",
            12,
            [
                "Аигел: трип-хоп сессия",
                "Аигел: концерт 07.11",
                "Аигел: концерт 09.11",
                "Аигел: концерт 12.11",
                "Аигел: концерт 13.11",
                "Аигел: концерт 16.11",
            ],
        ),
    ],
)
def test_concerts_search(query, expected_count, page_titles):
    response = client.get("/concerts/", {"q": query})
    assert response.status_code == 200
    assert response.context["query"] == query
    assert response.context["total_count"] == expected_count
    assert _concert_titles(response) == page_titles


def test_concerts_search_without_results():
    response = client.get("/concerts/", {"q": "Нет такого концерта"})
    assert response.status_code == 200
    assert response.context["total_count"] == 0
    assert "Концерты не найдены." in _content(response)


def test_concerts_filter_status_active():
    response = client.get("/concerts/", {"status": "active"})
    assert response.status_code == 200
    assert response.context["selected_status"] == "active"
    assert response.context["total_count"] == 99
    assert "Отменено" not in _content(response)


def test_concerts_filter_status_cancelled(cancelled_concert):
    response = client.get("/concerts/", {"status": "cancelled"})
    assert response.status_code == 200
    assert response.context["selected_status"] == "cancelled"
    assert response.context["total_count"] == 14
    content = _content(response)
    assert "Клубный вечер с Мейби Бейби" in content
    assert "Отменено" in content


def test_concerts_filter_by_venue():
    response = client.get("/concerts/", {"venue": "1"})
    assert response.status_code == 200
    assert response.context["selected_venue"] == "1"
    assert response.context["total_count"] == 13
    assert _concert_titles(response) == [
        "Клубный вечер с Мейби Бейби",
        "Буерак: концерт 01.11",
        "ЛСП: концерт 03.11",
        "Свидание: концерт 05.11",
        "Звери: концерт 06.11",
        "Мумий Тролль: концерт 08.11",
    ]


def test_concerts_filter_by_performer():
    response = client.get("/concerts/", {"performer": "1"})
    assert response.status_code == 200
    assert response.context["selected_performer"] == "1"
    assert response.context["total_count"] == 9
    assert _concert_titles(response) == [
        "Клубный вечер с Мейби Бейби",
        "Мейби Бейби в Питере",
        "Мейби Бейби: концерт 08.11",
        "Мейби Бейби: концерт 09.11",
        "Мейби Бейби: концерт 11.11",
        "Мейби Бейби: концерт 26.11",
    ]


def test_concerts_sort_by_venue():
    response = client.get("/concerts/", {"sort": "venue"})
    assert response.status_code == 200
    assert response.context["sort"] == "venue"
    assert _concert_titles(response) == [
        "Буерак: пост-панк ночь",
        "Буерак: концерт 21.11",
        "Пошлая Молли: концерт 04.11",
        "Дора: концерт 03.11",
        "Пошлая Молли: концерт 23.11",
        "Аигел: концерт 09.11",
    ]


def test_concerts_date_from_filter():
    response = client.get("/concerts/", {"date_from": "2026-11-01"})
    assert response.status_code == 200
    assert response.context["total_count"] == 149
    assert _concert_titles(response) == [
        "Буерак: концерт 01.11",
        "Мот: концерт 01.11",
        "Звери: концерт 01.11",
        "Мумий Тролль: концерт 01.11",
        "Пошлая Молли: концерт 02.11",
        "Мот: концерт 02.11",
    ]
    assert "Клубный вечер с Мейби Бейби" not in _content(response)


def test_concerts_invalid_date_from_shows_error():
    response = client.get("/concerts/", {"date_from": "31-12-2026"})
    assert response.status_code == 200
    assert response.context["error"] == (
        "Укажите корректную дату в формате ГГГГ-ММ-ДД."
    )
    assert "Укажите корректную дату" in _content(response)
    # Некорректная дата не должна отбрасывать остальные концерты.
    assert response.context["total_count"] == 159


# --- Статистика ---


def test_statistics_page_aggregates():
    response = client.get("/concerts/statistics/")
    assert response.status_code == 200
    content = _content(response)
    assert "Статистика концертов" in content

    overall = response.context["overall"]
    assert overall["total"] == 159
    assert overall["guests"] == 510063
    assert overall["min_price"] == Decimal("10.50")
    assert overall["max_price"] == Decimal("2500")
    assert '<p class="display-6">159</p>' in content
    assert '<p class="display-6">510063</p>' in content

    status_counts = response.context["status_counts"]
    assert status_counts == {
        "scheduled": 99,
        "cancelled": 13,
        "completed": 47,
    }

    by_status = {row["status"]: row for row in response.context["by_status"]}
    assert set(by_status) == {
        Concert.Status.SCHEDULED,
        Concert.Status.CANCELLED,
        Concert.Status.COMPLETED,
    }
    assert by_status[Concert.Status.SCHEDULED]["count"] == 99
    assert by_status[Concert.Status.CANCELLED]["count"] == 13
    assert by_status[Concert.Status.COMPLETED]["count"] == 47
    assert "Запланированные" in content
    assert "Завершённые" in content
    assert "Отменённые" in content

    venue_stats = response.context["venue_stats"]
    busy_venue = venue_stats.get(pk=1)
    assert busy_venue.total_count == 13
    assert busy_venue.active_count == 6
    assert busy_venue.guests == 13744
    empty_venue = venue_stats.get(pk=12)
    assert empty_venue.total_count == 12
    assert empty_venue.active_count == 8

    performer_stats = list(response.context["performer_stats"])
    assert len(performer_stats) == 5
    assert [item.concerts_count for item in performer_stats[:3]] == [19, 18, 17]
    assert "Ведущие исполнители по числу концертов" in content


# --- Свободные площадки ---


def test_available_venues_excludes_busy_venue(venue1_future_concert):
    response = client.get("/venues/available/", {"date": "2099-03-01"})
    assert response.status_code == 200
    content = _content(response)
    assert "Дата: 2099-03-01" in content
    assert "Adrenaline Stadium" not in content
    assert "Главclub Green Concert" in content
    assert response.context["venues"].count() == 11


def test_available_venues_invalid_date_shows_error():
    response = client.get("/venues/available/", {"date": "not-a-date"})
    assert response.status_code == 200
    assert response.context["error"] == "Укажите корректную дату."
    assert "Укажите корректную дату." in _content(response)


def test_available_venues_without_date():
    response = client.get("/venues/available/")
    assert response.status_code == 200
    assert response.context["error"] is None
    assert response.context["venues"].count() == 0


def test_available_venues_ignores_cancelled_concert(venue1_future_concert):
    venue1_future_concert.cancel()
    response = client.get("/venues/available/", {"date": "2099-03-01"})
    assert response.status_code == 200
    assert "Adrenaline Stadium" in _content(response)
    assert response.context["venues"].count() == 12


def test_available_venues_ignores_completed_concert(venue1_future_concert):
    venue1_future_concert.status = Concert.Status.COMPLETED
    venue1_future_concert.save(update_fields=["status"])
    response = client.get("/venues/available/", {"date": "2099-03-01"})
    assert response.status_code == 200
    assert "Adrenaline Stadium" in _content(response)
    assert response.context["venues"].count() == 12


# --- Списки исполнителей, площадок и программ ---


def test_performers_search():
    response = client.get("/performers/", {"q": "Мейби"})
    assert response.status_code == 200
    assert response.context["query"] == "Мейби"
    assert response.context["total_count"] == 1
    assert "Мейби Бейби" in _content(response)


def test_performers_search_by_genre():
    response = client.get("/performers/", {"q": "хип-хоп"})
    assert response.status_code == 200
    assert response.context["total_count"] == 2
    content = _content(response)
    assert "ЛСП" in content
    assert "Мот" in content


def test_venues_min_capacity_filter():
    response = client.get("/venues/", {"min_capacity": "5000"})
    assert response.status_code == 200
    assert response.context["min_capacity"] == "5000"
    assert response.context["total_count"] == 4
    content = _content(response)
    for venue_name in (
        "Adrenaline Stadium",
        "Stadium Live",
        "СК Олимпийский",
        "Crocus City Hall",
    ):
        assert venue_name in content
    assert "Главclub Green Concert" not in content


def test_venues_search_by_city():
    response = client.get("/venues/", {"q": "Екатеринбург"})
    assert response.status_code == 200
    assert response.context["total_count"] == 1
    assert "Телеклуб" in _content(response)


def test_programs_max_age_filter():
    response = client.get("/programs/", {"max_age": "12"})
    assert response.status_code == 200
    assert response.context["max_age"] == "12"
    assert response.context["total_count"] == 5
    content = _content(response)
    for program_name in (
        "Хиты Мумий Тролль",
        "Вечер инди-рока",
        "Акустический вечер",
        "Золотые хиты 2000-х",
        "Семейный концерт",
    ):
        assert program_name in content
    assert "Рэп-симфония" not in content


def test_programs_search():
    response = client.get("/programs/", {"q": "Мумий"})
    assert response.status_code == 200
    assert response.context["total_count"] == 1
    assert "Хиты Мумий Тролль" in _content(response)
