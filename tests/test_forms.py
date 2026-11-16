"""Тесты форм ПР11: фильтр концертов, создание/редактирование/отмена,
загрузка изображений площадок."""

from datetime import date
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django import forms

from concerts.forms import ConcertFilterForm, ConcertForm
from concerts.models import Concert
from venues.forms import VenueForm
from venues.models import Venue

client = Client()

FUTURE_DATE = "2099-05-01"
OTHER_FUTURE_DATE = "2099-06-02"

# Валидный PNG 1x1 (содержит IDAT): проходит проверку Pillow/Django.
PNG_BYTES = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
    b'\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS'
    b'\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00'
    b'\x00\x03\x01\x01\x00\xc9\xfe\x92\xef\x00\x00\x00\x00IEN'
    b'D\xaeB`\x82'
)


def _content(response) -> str:
    """Вернуть HTML-код ответа строкой."""
    return response.content.decode()


def _concert_data(**overrides):
    """Подготовить валидные данные формы концерта."""
    data = {
        "title": "Тестовый концерт ПР11",
        "performer": "1",
        "venue": "5",
        "program": "1",
        "date": FUTURE_DATE,
        "expected_guests": "500",
        "base_ticket_price": "1500.00",
    }
    data.update(overrides)
    return data


@pytest.fixture
def scheduled_concert():
    """Создать запланированный концерт на площадке 5 в далёком будущем."""
    concert = Concert.objects.create(
        title="ПР11: редактируемый концерт",
        performer_id=1,
        venue_id=5,
        program_id=1,
        date=date(2099, 6, 1),
        expected_guests=500,
        base_ticket_price=Decimal("1500.00"),
    )
    try:
        yield concert
    finally:
        concert.delete()


@pytest.fixture
def conflicting_concert():
    """Создать запланированный концерт на площадке 5 на другую дату."""
    concert = Concert.objects.create(
        title="ПР11: конфликтующий концерт",
        performer_id=2,
        venue_id=5,
        program_id=1,
        date=date(2099, 6, 2),
        expected_guests=100,
        base_ticket_price=Decimal("900.00"),
    )
    try:
        yield concert
    finally:
        concert.delete()


@pytest.fixture
def media_root(tmp_path, settings):
    """Перенаправить MEDIA_ROOT во временную директорию pytest."""
    settings.MEDIA_ROOT = tmp_path
    return tmp_path


# --- Классы форм ---


def test_filter_form_fields_and_choices():
    """ConcertFilterForm содержит все поля с корректными choices."""
    form = ConcertFilterForm()
    for name in (
        "q",
        "venue",
        "performer",
        "status",
        "date_from",
        "sort",
    ):
        assert name in form.fields
    for name in ("q", "venue", "performer", "status", "date_from", "sort"):
        assert form.fields[name].required is False
    assert isinstance(form.fields["venue"], forms.ModelChoiceField)
    assert isinstance(form.fields["performer"], forms.ModelChoiceField)
    status_values = [value for value, _ in form.fields["status"].choices]
    assert status_values == ["", "active", "cancelled"]
    sort_values = [value for value, _ in form.fields["sort"].choices]
    assert sort_values == ["", "date", "title", "venue", "performer"]


def test_concert_form_model_and_fields():
    """ConcertForm — ModelForm для Concert с нужным набором полей."""
    assert ConcertForm.Meta.model is Concert
    assert list(ConcertForm.Meta.fields) == [
        "title",
        "performer",
        "venue",
        "program",
        "date",
        "expected_guests",
        "base_ticket_price",
    ]


def test_concert_form_clean_date_rejects_past():
    """clean_date отклоняет прошедшую дату."""
    form = ConcertForm(_concert_data(date="2020-01-01"))
    assert not form.is_valid()
    assert "прошедшую дату" in str(form.errors["date"])


def test_concert_form_capacity_error():
    """clean() добавляет ошибку expected_guests при превышении вместимости."""
    # Площадка 5 (Известия Hall) вмещает 1100 зрителей.
    form = ConcertForm(_concert_data(expected_guests="5000"))
    assert not form.is_valid()
    assert "не вмещает" in str(form.errors["expected_guests"])


# --- Создание концерта ---


def test_concert_create_get_ok():
    """GET /concerts/create/ отдаёт страницу с формой."""
    response = client.get("/concerts/create/")
    assert response.status_code == 200


def test_concert_create_valid_redirects_and_creates():
    """Валидный POST создаёт концерт со статусом SCHEDULED и редиректит."""
    before = Concert.objects.count()
    response = client.post("/concerts/create/", _concert_data())
    assert response.status_code == 302
    assert response.url == "/concerts/"
    concert = Concert.objects.get(title="Тестовый концерт ПР11")
    try:
        assert Concert.objects.count() == before + 1
        assert concert.status == Concert.Status.SCHEDULED
        assert concert.venue_id == 5
    finally:
        concert.delete()


def test_concert_create_past_date_shows_error():
    """POST с прошедшей датой возвращает форму с ошибкой, концерт не создан."""
    before = Concert.objects.count()
    response = client.post("/concerts/create/", _concert_data(date="2020-01-01"))
    assert response.status_code == 200
    assert "прошедшую дату" in _content(response)
    assert Concert.objects.count() == before


def test_concert_create_busy_venue_shows_error(scheduled_concert):
    """POST на площадку с запланированным концертом в эту дату отклоняется."""
    before = Concert.objects.count()
    data = _concert_data(date="2099-06-01")
    response = client.post("/concerts/create/", data)
    assert response.status_code == 200
    assert "уже занята" in _content(response)
    assert Concert.objects.count() == before


def test_concert_create_cancelled_concert_does_not_block():
    """Отменённый концерт в эту дату не мешает созданию нового."""
    concert = Concert.objects.create(
        title="ПР11: отменённый на дату",
        performer_id=1,
        venue_id=5,
        program_id=1,
        date=date(2099, 5, 10),
        expected_guests=100,
        base_ticket_price=Decimal("900.00"),
        status=Concert.Status.CANCELLED,
    )
    try:
        response = client.post(
            "/concerts/create/", _concert_data(date="2099-05-10")
        )
        assert response.status_code == 302
        created = Concert.objects.get(title="Тестовый концерт ПР11")
        assert created.status == Concert.Status.SCHEDULED
        created.delete()
    finally:
        concert.delete()


def test_concert_create_capacity_overflow_shows_error():
    """POST с зрителями больше вместимости возвращает ошибку формы."""
    before = Concert.objects.count()
    response = client.post("/concerts/create/", _concert_data(expected_guests="5000"))
    assert response.status_code == 200
    assert "не вмещает" in _content(response)
    assert Concert.objects.count() == before


# --- Редактирование концерта ---


def test_concert_update_get_shows_current_values(scheduled_concert):
    """GET /concerts/<id>/edit/ отдаёт форму с текущими значениями."""
    response = client.get(f"/concerts/{scheduled_concert.pk}/edit/")
    assert response.status_code == 200
    content = _content(response)
    assert "ПР11: редактируемый концерт" in content
    assert 'value="2099-06-01"' in content


def test_concert_update_valid_post(scheduled_concert):
    """Валидный POST обновляет объект на месте, новая строка не создаётся."""
    before = Concert.objects.count()
    response = client.post(
        f"/concerts/{scheduled_concert.pk}/edit/",
        _concert_data(title="ПР11: новое название", date="2099-06-01"),
    )
    assert response.status_code == 302
    scheduled_concert.refresh_from_db()
    assert scheduled_concert.pk is not None
    assert scheduled_concert.title == "ПР11: новое название"
    assert Concert.objects.count() == before


def test_concert_update_unchanged_data_no_conflict(scheduled_concert):
    """POST без изменений проходит без ложного конфликта занятости."""
    data = _concert_data(
        title="ПР11: редактируемый концерт", date="2099-06-01"
    )
    response = client.post(f"/concerts/{scheduled_concert.pk}/edit/", data)
    assert response.status_code == 302


def test_concert_update_conflict_with_other_concert(
    scheduled_concert, conflicting_concert
):
    """Перенос на дату другого запланированного концерта отклоняется."""
    response = client.post(
        f"/concerts/{scheduled_concert.pk}/edit/",
        _concert_data(title="ПР11: редактируемый концерт", date=OTHER_FUTURE_DATE),
    )
    assert response.status_code == 200
    assert "уже занята" in _content(response)
    scheduled_concert.refresh_from_db()
    assert scheduled_concert.date == date(2099, 6, 1)


def test_concert_update_completed_concert_404():
    """Редактирование завершённого концерта запрещено (404)."""
    original_status = Concert.objects.filter(pk=1).values_list(
        "status", flat=True
    ).get()
    Concert.objects.filter(pk=1).update(status=Concert.Status.COMPLETED)
    try:
        assert client.get("/concerts/1/edit/").status_code == 404
    finally:
        Concert.objects.filter(pk=1).update(status=original_status)


def test_concert_update_cancelled_concert_404(scheduled_concert):
    """Редактирование отменённого концерта запрещено (404)."""
    scheduled_concert.cancel()
    assert client.get(f"/concerts/{scheduled_concert.pk}/edit/").status_code == 404


# --- Отмена концерта ---


def test_concert_cancel_flow(scheduled_concert):
    """POST /cancel/ отменяет концерт; GET — 405; повторный POST — 404."""
    response = client.post(f"/concerts/{scheduled_concert.pk}/cancel/")
    assert response.status_code == 302
    scheduled_concert.refresh_from_db()
    assert scheduled_concert.status == Concert.Status.CANCELLED
    assert Concert.objects.filter(pk=scheduled_concert.pk).exists()

    assert client.get(f"/concerts/{scheduled_concert.pk}/cancel/").status_code == 405
    assert client.post(f"/concerts/{scheduled_concert.pk}/cancel/").status_code == 404


def test_concert_cancel_completed_concert_404():
    """Отмена завершённого концерта запрещена (404)."""
    original_status = Concert.objects.filter(pk=1).values_list(
        "status", flat=True
    ).get()
    Concert.objects.filter(pk=1).update(status=Concert.Status.COMPLETED)
    try:
        response = client.post("/concerts/1/cancel/")
        assert response.status_code == 404
    finally:
        Concert.objects.filter(pk=1).update(status=original_status)


# --- Фильтр на списке концертов ---


@pytest.mark.parametrize(
    "params",
    [
        {"date_from": "не_дата"},
        {"venue": "999999"},
        {"sort": "unknown"},
    ],
)
def test_concerts_filter_bad_params_show_error(params):
    """Некорректные параметры фильтра не дают 500 и показывают ошибку."""
    response = client.get("/concerts/", params)
    assert response.status_code == 200
    assert "Проверьте введённые значения фильтров" in _content(response)


def test_concerts_filter_valid_venue_filters(scheduled_concert):
    """Валидный фильтр ?venue=<pk> фильтрует список концертов."""
    response = client.get("/concerts/", {"venue": "5"})
    assert response.status_code == 200
    # Концерт на 2099-06-01 окажется на последней странице:
    # в данных уже есть концерты площадки 5 с датами 2026 года.
    last_page = response.context["page_obj"].paginator.num_pages
    last = client.get("/concerts/", {"venue": "5", "page": last_page})
    assert last.status_code == 200
    assert "ПР11: редактируемый концерт" in _content(last)


# --- VenueForm и загрузка изображений ---


def test_venue_form_fields():
    """VenueForm — ModelForm с полями name/city/capacity/image."""
    assert VenueForm.Meta.model is Venue
    assert list(VenueForm.Meta.fields) == ["name", "city", "capacity", "image"]


def test_venue_create_get_ok():
    """GET /venues/create/ отдаёт страницу с формой."""
    response = client.get("/venues/create/")
    assert response.status_code == 200


def test_venue_create_without_image(media_root):
    """POST без изображения тоже создаёт площадку (blank=True)."""
    before = Venue.objects.count()
    response = client.post(
        "/venues/create/",
        {"name": "ПР11 Площадка без фото", "city": "Москва", "capacity": "100"},
    )
    assert response.status_code == 302
    assert Venue.objects.count() == before + 1
    venue = Venue.objects.get(name="ПР11 Площадка без фото")
    assert venue.slug
    # Убираем тестовую запись, чтобы не сдвигать счётчики других тестов.
    venue.delete()


def test_venue_create_with_image(media_root):
    """POST с PNG создаёт площадку, файл сохраняется в MEDIA_ROOT."""
    image = SimpleUploadedFile("pr11.png", PNG_BYTES, content_type="image/png")
    response = client.post(
        "/venues/create/",
        {
            "name": "ПР11 Площадка с фото",
            "city": "Санкт-Петербург",
            "capacity": "200",
            "image": image,
        },
    )
    assert response.status_code == 302
    venue = Venue.objects.get(name="ПР11 Площадка с фото")
    assert venue.image
    assert (media_root / venue.image.name).exists()

    detail = client.get(f"/venues/{venue.slug}/")
    assert detail.status_code == 200
    assert venue.image.url in _content(detail)
    venue.image.delete(save=False)
    venue.delete()
