"""ORM-тесты моделей, связей и запросов (ПР9)."""

from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import pytest
from django.apps import apps
from django.core.management import call_command
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Avg, Count, Max, Min, ProtectedError, Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.test.utils import CaptureQueriesContext

from concerts.models import Concert
from performers.models import Performer
from programs.models import Program
from venues.models import Venue


@pytest.fixture
def factory():
    """Создавать объекты с уникальными id и удалять их после теста."""
    created = {"concerts": [], "programs": [], "venues": [], "performers": []}
    next_pk = {"value": 901}

    def take_pk(pk):
        if pk is None:
            pk = next_pk["value"]
            next_pk["value"] += 1
        return pk

    def make_performer(
        pk=None,
        name="Тестовый исполнитель",
        genre="поп",
        rating="8.0",
    ):
        obj = Performer.objects.create(
            pk=take_pk(pk),
            name=name,
            genre=genre,
            rating=Decimal(str(rating)),
        )
        created["performers"].append(obj.pk)
        return obj

    def make_venue(
        pk=None,
        name="Тестовая площадка",
        city="Москва",
        capacity=5000,
    ):
        obj = Venue.objects.create(
            pk=take_pk(pk),
            name=name,
            city=city,
            capacity=capacity,
        )
        created["venues"].append(obj.pk)
        return obj

    def make_program(
        pk=None,
        name="Тестовая программа",
        duration=90,
        age_limit=12,
    ):
        obj = Program.objects.create(
            pk=take_pk(pk),
            name=name,
            duration=duration,
            age_limit=age_limit,
        )
        created["programs"].append(obj.pk)
        return obj

    def make_concert(
        pk=None,
        *,
        performer,
        venue,
        program,
        title="Тестовый концерт",
        concert_date=date(2027, 1, 1),
        expected_guests=100,
        base_ticket_price="1000.00",
        status=Concert.Status.SCHEDULED,
    ):
        obj = Concert.objects.create(
            pk=take_pk(pk),
            title=title,
            performer=performer,
            venue=venue,
            program=program,
            date=concert_date,
            expected_guests=expected_guests,
            base_ticket_price=Decimal(str(base_ticket_price)),
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

    # Удаляем в порядке, обратном зависимостям, чтобы не мешать PROTECT.
    Concert.objects.filter(pk__in=created["concerts"]).delete()
    Program.objects.filter(pk__in=created["programs"]).delete()
    Venue.objects.filter(pk__in=created["venues"]).delete()
    Performer.objects.filter(pk__in=created["performers"]).delete()


def _create_concert(factory, **options):
    """Создать концерт, при необходимости вместе со связанными объектами."""
    performer = options.pop("performer", None)
    venue = options.pop("venue", None)
    program = options.pop("program", None)
    if performer is None:
        performer = factory.make_performer()
    if venue is None:
        venue = factory.make_venue()
    if program is None:
        program = factory.make_program()
    return factory.make_concert(
        performer=performer,
        venue=venue,
        program=program,
        **options,
    )


# --- Регистрация моделей и метаданные ---


def test_models_registered_in_apps_registry():
    assert apps.get_model("performers", "Performer") is Performer
    assert apps.get_model("venues", "Venue") is Venue
    assert apps.get_model("programs", "Program") is Program
    assert apps.get_model("concerts", "Concert") is Concert
    assert Performer._meta.app_label == "performers"
    assert Concert._meta.app_label == "concerts"
    assert Performer._meta.db_table == "performers_performer"
    assert Venue._meta.db_table == "venues_venue"
    assert Program._meta.db_table == "programs_program"
    assert Concert._meta.db_table == "concerts_concert"


def test_meta_ordering_declaration():
    assert Performer._meta.ordering == ["name"]
    assert Venue._meta.ordering == ["name"]
    assert Program._meta.ordering == ["name"]
    assert Concert._meta.ordering == ["date", "pk"]


def test_default_queryset_ordering():
    names = list(Performer.objects.values_list("name", flat=True))
    assert names == sorted(names)
    venue_names = list(Venue.objects.values_list("name", flat=True))
    assert venue_names == sorted(venue_names)
    program_names = list(Program.objects.values_list("name", flat=True))
    assert program_names == sorted(program_names)
    concert_pks = list(Concert.objects.values_list("pk", flat=True))
    expected = list(
        Concert.objects.order_by("date", "pk").values_list("pk", flat=True)
    )
    assert concert_pks == expected


# --- Строковые представления ---


def test_performer_str():
    assert str(Performer.objects.get(pk=1)) == "Мейби Бейби (гиперпоп)"


def test_venue_str():
    assert str(Venue.objects.get(pk=1)) == (
        "Adrenaline Stadium, Москва (5000 мест)"
    )


def test_program_str():
    assert str(Program.objects.get(pk=1)) == "MAYDAY: клубный сет, 90 мин"


def test_concert_str():
    assert str(Concert.objects.get(pk=1)) == (
        "Клубный вечер с Мейби Бейби (15.10.2026)"
    )


# --- Методы моделей ---


def test_venue_is_suitable_for_boundaries():
    venue = Venue.objects.get(pk=1)
    assert venue.capacity == 5000
    assert venue.is_suitable_for(0) is True
    assert venue.is_suitable_for(4999) is True
    assert venue.is_suitable_for(5000) is True
    assert venue.is_suitable_for(5001) is False


def test_program_is_allowed_for_boundaries():
    program = Program.objects.get(pk=1)
    assert program.age_limit == 16
    assert program.is_allowed_for(15) is False
    assert program.is_allowed_for(16) is True
    assert program.is_allowed_for(18) is True


@pytest.mark.parametrize(
    ("rating", "expected_price"),
    [
        ("9.5", Decimal("1500.00")),
        ("9.0", Decimal("1500.00")),
        ("8.9", Decimal("1200.00")),
        ("7.0", Decimal("1200.00")),
        ("6.9", Decimal("1000.00")),
    ],
)
def test_calculate_ticket_price_by_rating(factory, rating, expected_price):
    performer = factory.make_performer(rating=rating)
    concert = _create_concert(
        factory,
        performer=performer,
        base_ticket_price="1000.00",
    )
    assert concert.calculate_ticket_price() == expected_price


def test_calculate_ticket_price_rounds_to_kopecks(factory):
    performer = factory.make_performer(rating="8.0")
    concert = _create_concert(
        factory,
        performer=performer,
        base_ticket_price="999.99",
    )
    assert concert.calculate_ticket_price() == Decimal("1199.99")


@pytest.mark.parametrize(
    ("capacity", "guests", "message"),
    [
        (5000, 4800, "Площадка подходит, свободных мест: 200"),
        (5000, 5000, "Площадка подходит, свободных мест: 0"),
        (1500, 1600, "Площадка не вмещает всех зрителей"),
    ],
)
def test_check_venue_fit(factory, capacity, guests, message):
    venue = factory.make_venue(capacity=capacity)
    concert = _create_concert(
        factory,
        venue=venue,
        expected_guests=guests,
    )
    assert concert.check_venue_fit() == message


def test_calculate_revenue(factory):
    performer = factory.make_performer(rating="9.5")
    concert = _create_concert(
        factory,
        performer=performer,
        expected_guests=100,
        base_ticket_price="1000.00",
    )
    assert concert.calculate_ticket_price() == Decimal("1500.00")
    assert concert.calculate_revenue() == Decimal("150000.00")


def test_concert_default_status_is_scheduled(factory):
    concert = _create_concert(factory)
    assert concert.status == Concert.Status.SCHEDULED
    assert concert.get_status_display() == "Запланирован"


def test_concert_status_choices_labels():
    assert Concert.Status.SCHEDULED.label == "Запланирован"
    assert Concert.Status.CANCELLED.label == "Отменён"
    assert Concert.Status.COMPLETED.label == "Завершён"


def test_cancelled_status_persisted(factory):
    concert = _create_concert(
        factory,
        status=Concert.Status.CANCELLED,
    )
    assert concert.get_status_display() == "Отменён"


def test_cancel_persists_and_saves_only_changed_field(factory):
    concert = _create_concert(factory, title="Исходный концерт")
    concert.title = "Название без сохранения"
    concert.cancel()
    concert.refresh_from_db()
    assert concert.status == Concert.Status.CANCELLED
    assert concert.title == "Исходный концерт"


# --- CRUD ---


def test_create_objects_with_explicit_ids(factory):
    performer = factory.make_performer(
        pk=951,
        name="Новый исполнитель",
        genre="джаз",
        rating="6.5",
    )
    venue = factory.make_venue(
        pk=952,
        name="Новая площадка",
        city="Казань",
        capacity=700,
    )
    program = factory.make_program(
        pk=953,
        name="Новая программа",
        duration=70,
        age_limit=12,
    )
    concert = factory.make_concert(
        pk=954,
        performer=performer,
        venue=venue,
        program=program,
        title="Новый концерт",
        concert_date=date(2027, 2, 1),
        expected_guests=500,
        base_ticket_price="900.00",
    )
    assert concert.pk == 954
    assert concert.performer_id == 951
    assert concert.venue_id == 952
    assert concert.program_id == 953
    assert len({performer.pk, venue.pk, program.pk, concert.pk}) == 4
    assert Performer.objects.get(pk=951).name == "Новый исполнитель"
    assert Venue.objects.get(pk=952).city == "Казань"
    assert Program.objects.get(pk=953).duration == 70
    assert Concert.objects.get(pk=954).title == "Новый концерт"


def test_update_object_via_save(factory):
    performer = factory.make_performer(rating="6.0")
    performer.rating = Decimal("7.4")
    performer.genre = "джаз"
    performer.save()
    refreshed = Performer.objects.get(pk=performer.pk)
    assert refreshed.rating == Decimal("7.4")
    assert refreshed.genre == "джаз"


def test_update_queryset(factory):
    performer = factory.make_performer(genre="поп")
    updated = Performer.objects.filter(pk=performer.pk).update(genre="рок")
    assert updated == 1
    performer.refresh_from_db()
    assert performer.genre == "рок"


def test_delete_object(factory):
    performer = factory.make_performer()
    venue = factory.make_venue()
    program = factory.make_program()
    concert = factory.make_concert(
        performer=performer,
        venue=venue,
        program=program,
    )
    concert_pk = concert.pk
    concert.delete()
    assert not Concert.objects.filter(pk=concert_pk).exists()
    # Связанные справочники после удаления концерта остаются на месте.
    assert Performer.objects.filter(pk=performer.pk).exists()
    assert Venue.objects.filter(pk=venue.pk).exists()
    assert Program.objects.filter(pk=program.pk).exists()


def test_protect_prevents_deleting_referenced_performer():
    performer = Performer.objects.get(pk=1)
    with pytest.raises(ProtectedError):
        performer.delete()
    assert Performer.objects.filter(pk=1).exists()


def test_protect_prevents_deleting_referenced_venue():
    venue = Venue.objects.get(pk=1)
    with pytest.raises(ProtectedError):
        venue.delete()
    assert Venue.objects.filter(pk=1).exists()


def test_protect_prevents_deleting_referenced_program():
    program = Program.objects.get(pk=1)
    with pytest.raises(ProtectedError):
        program.delete()
    assert Program.objects.filter(pk=1).exists()


# --- Связи ---


def test_concert_forward_relations():
    concert = Concert.objects.get(pk=1)
    assert concert.performer_id == 1
    assert concert.venue_id == 1
    assert concert.program_id == 1
    assert isinstance(concert.performer, Performer)
    assert isinstance(concert.venue, Venue)
    assert isinstance(concert.program, Program)
    assert concert.performer.name == "Мейби Бейби"
    assert concert.venue.name == "Adrenaline Stadium"
    assert concert.program.name == "MAYDAY: клубный сет"


def test_related_name_concerts():
    for field_name, model in (
        ("performer", Performer),
        ("venue", Venue),
        ("program", Program),
    ):
        field = Concert._meta.get_field(field_name)
        assert field.remote_field.get_accessor_name() == "concerts"
        assert model._meta.get_field("concerts").related_model is Concert


def test_reverse_relations_from_performer():
    performer = Performer.objects.get(pk=1)
    manager = performer.concerts
    assert manager.model is Concert
    assert list(manager.order_by("pk").values_list("pk", flat=True)) == [
        1,
        13,
        48,
        81,
        100,
        104,
        105,
        109,
        146,
    ]


def test_reverse_relations_from_venue_and_program():
    venue = Venue.objects.get(pk=1)
    assert sorted(venue.concerts.values_list("pk", flat=True)) == [
        1,
        40,
        41,
        42,
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
    ]
    program = Program.objects.get(pk=3)
    assert list(program.concerts.order_by("pk").values_list("pk", flat=True)) == [
        2,
        5,
        20,
        32,
        33,
        41,
        53,
        54,
        66,
        91,
        107,
        122,
        135,
    ]


def test_select_related_loads_related_objects_in_one_query():
    connection.ensure_connection()
    with CaptureQueriesContext(connection) as captured:
        concert = Concert.objects.select_related(
            "performer",
            "venue",
            "program",
        ).get(pk=1)
        values = (
            concert.performer.name,
            concert.venue.name,
            concert.program.name,
        )
    assert values == (
        "Мейби Бейби",
        "Adrenaline Stadium",
        "MAYDAY: клубный сет",
    )
    assert len(captured.captured_queries) == 1


def test_without_select_related_issues_extra_queries():
    connection.ensure_connection()
    with CaptureQueriesContext(connection) as captured:
        concert = Concert.objects.get(pk=1)
        _ = concert.performer.name
        _ = concert.venue.name
        _ = concert.program.name
    # Один запрос на концерт и по одному на каждую связанную модель.
    assert len(captured.captured_queries) == 4


def test_prefetch_related_loads_concerts_in_two_queries():
    connection.ensure_connection()
    with CaptureQueriesContext(connection) as captured:
        venues = list(Venue.objects.prefetch_related("concerts").order_by("pk"))
        counts = [len(venue.concerts.all()) for venue in venues]
    assert len(captured.captured_queries) == 2
    assert len(counts) == 12
    assert counts[0] == 13
    assert counts[11] == 12
    assert sum(counts) == 159


# --- Запросы ---


def test_queryset_all_and_counts():
    assert Concert.objects.count() == 159
    assert Performer.objects.count() == 12
    assert Venue.objects.count() == 12
    assert Program.objects.count() == 12
    assert len(list(Concert.objects.all())) == 159


def test_filter_single_and_multiple_conditions():
    assert Concert.objects.filter(venue_id=1).count() == 13
    assert (
        Concert.objects.filter(
            venue_id=3,
            status=Concert.Status.SCHEDULED,
        ).count()
        == 10
    )
    assert (
        Concert.objects.filter(status=Concert.Status.CANCELLED).count() == 13
    )
    assert Concert.objects.filter(date__gte=date(2026, 11, 1)).count() == 149
    assert Concert.objects.filter(expected_guests__gte=5000).count() == 24


def test_filter_by_related_field_city():
    moscow = Concert.objects.filter(venue__city="Москва")
    assert moscow.count() == 107
    assert {1, 3, 4, 6}.issubset(
        set(moscow.values_list("pk", flat=True))
    )


def test_exclude_by_related_field_city():
    not_moscow = Concert.objects.exclude(venue__city="Москва")
    assert not_moscow.count() == 52
    assert {2, 5, 7, 13}.issubset(
        set(not_moscow.values_list("pk", flat=True))
    )


def test_get_and_get_object_or_404():
    concert = Concert.objects.get(pk=1)
    assert concert.title == "Клубный вечер с Мейби Бейби"
    assert get_object_or_404(Concert, pk=1).pk == 1
    with pytest.raises(Concert.DoesNotExist):
        Concert.objects.get(pk=999)
    with pytest.raises(Http404):
        get_object_or_404(Concert, pk=999)


def test_icontains_search():
    by_title = Concert.objects.filter(title__icontains="Мейби")
    assert set(by_title.values_list("pk", flat=True)) == {
        1,
        13,
        48,
        81,
        100,
        104,
        105,
        109,
        146,
    }
    by_performer = Concert.objects.filter(performer__name__icontains="Аигел")
    performer_pks = set(by_performer.values_list("pk", flat=True))
    assert len(performer_pks) == 12
    assert {12, 14}.issubset(performer_pks)


def test_q_or_search():
    result = Concert.objects.filter(
        Q(title__icontains="Дора") | Q(performer__name__icontains="Звери")
    )
    result_pks = set(result.values_list("pk", flat=True))
    assert len(result_pks) == 23
    assert {2, 9, 15}.issubset(result_pks)


def test_order_by_single_field():
    assert Performer.objects.order_by("rating").first().name == "Пошлая Молли"
    assert (
        Performer.objects.order_by("-rating").first().name == "Мейби Бейби"
    )
    assert Program.objects.order_by("-duration").first().duration == 120


def test_order_by_multiple_fields():
    assert Concert.objects.order_by("date", "pk").first().pk == 5
    assert (
        Program.objects.order_by("duration", "name").first().name
        == "Семейный концерт"
    )
    rated = list(
        Performer.objects.order_by("rating", "name").values_list(
            "rating",
            "name",
        )
    )
    assert rated == sorted(rated)


def test_values():
    row = Concert.objects.filter(pk=1).values(
        "title",
        "expected_guests",
        "status",
    ).get()
    assert row == {
        "title": "Клубный вечер с Мейби Бейби",
        "expected_guests": 4800,
        "status": "COMPLETED",
    }


def test_values_list_flat():
    names = list(Venue.objects.order_by("pk").values_list("name", flat=True))
    assert len(names) == 12
    assert names[0] == "Adrenaline Stadium"
    pairs = list(
        Concert.objects.filter(pk=1).values_list("pk", "expected_guests")
    )
    assert pairs == [(1, 4800)]


def test_annotate_count_with_q_filter():
    stats = Venue.objects.annotate(
        total=Count("concerts"),
        active=Count(
            "concerts",
            filter=Q(concerts__status=Concert.Status.SCHEDULED),
        ),
        cancelled=Count(
            "concerts",
            filter=Q(concerts__status=Concert.Status.CANCELLED),
        ),
    ).get(pk=1)
    assert (stats.total, stats.active, stats.cancelled) == (13, 6, 1)
    empty = Venue.objects.annotate(total=Count("concerts")).get(pk=12)
    assert empty.total == 12


def test_annotate_with_aggregate_over_related():
    performer = (
        Performer.objects.filter(pk=1)
        .annotate(total_guests=Sum("concerts__expected_guests"))
        .get()
    )
    assert performer.total_guests == 35652
    venue = (
        Venue.objects.filter(pk=1)
        .annotate(total_guests=Sum("concerts__expected_guests"))
        .get()
    )
    assert venue.total_guests == 32055


def test_aggregate_statistics():
    aggregate = Concert.objects.aggregate(
        total=Count("pk"),
        guests=Sum("expected_guests"),
        min_price=Min("base_ticket_price"),
        max_price=Max("base_ticket_price"),
        avg_price=Avg("base_ticket_price"),
    )
    assert aggregate["total"] == 159
    assert aggregate["guests"] == 510063
    assert aggregate["min_price"] == Decimal("10.50")
    assert aggregate["max_price"] == Decimal("2500")
    assert float(aggregate["avg_price"]) == pytest.approx(217.35220125786162)


def test_paginator_pages():
    queryset = Concert.objects.order_by("date", "pk")
    paginator = Paginator(queryset, 6)
    assert paginator.count == 159
    assert paginator.num_pages == 27
    assert [item.pk for item in paginator.page(1)] == [5, 4, 15, 6, 7, 11]
    assert [item.pk for item in paginator.page(2)] == [1, 12, 2, 13, 45, 62]
    assert [item.pk for item in paginator.page(3)] == [114, 133, 24, 76, 110, 132]
    assert [item.pk for item in paginator.page(27)] == [95, 14, 10]


# --- Миграции ---


def test_no_pending_migrations():
    try:
        call_command(
            "makemigrations",
            "--check",
            "--dry-run",
            verbosity=0,
        )
    except SystemExit as error:
        pytest.fail(f"Обнаружены неприменённые миграции: {error}")
