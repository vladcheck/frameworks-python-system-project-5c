"""Представления приложения concerts: ORM, фильтры, сортировка, пагинация."""

from datetime import date, datetime

from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from performers.models import Performer
from venues.models import Venue

from .models import Concert

# Белый список параметров сортировки: URL -> поле модели.
SORT_FIELDS = {
    "date": "date",
    "title": "title",
    "venue": "venue__name",
    "performer": "performer__name",
}

# Белый список фильтров по статусу концерта.
STATUS_FILTERS = {
    "active": False,
    "cancelled": True,
}

PAGE_SIZE = 6


def _parse_date(value: str):
    """Преобразовать строку ГГГГ-ММ-ДД в объект date или вернуть None."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def concerts(request: HttpRequest):
    """Показать список концертов с поиском, фильтрами, сортировкой и страницами."""
    query = request.GET.get("q", "").strip()
    venue_id = request.GET.get("venue", "").strip()
    performer_id = request.GET.get("performer", "").strip()
    status = request.GET.get("status", "").strip()
    date_from = request.GET.get("date_from", "").strip()
    sort = request.GET.get("sort", "date")
    error = None

    # select_related() загружает связанные объекты одним запросом.
    concerts_qs = Concert.objects.select_related(
        "performer", "venue", "program"
    )

    if query:
        # Поиск по названию концерта и по имени связанного исполнителя.
        concerts_qs = concerts_qs.filter(
            Q(title__icontains=query) | Q(performer__name__icontains=query)
        )
    if venue_id.isdigit():
        # Фильтрация по полю связанной модели (внешний ключ).
        concerts_qs = concerts_qs.filter(venue_id=int(venue_id))
    if performer_id.isdigit():
        concerts_qs = concerts_qs.filter(performer_id=int(performer_id))
    if status in STATUS_FILTERS:
        concerts_qs = concerts_qs.filter(is_cancelled=STATUS_FILTERS[status])
    if date_from:
        parsed_date = _parse_date(date_from)
        if parsed_date is None:
            error = "Укажите корректную дату в формате ГГГГ-ММ-ДД."
        else:
            concerts_qs = concerts_qs.filter(date__gte=parsed_date)

    # Поле сортировки берётся из белого списка, а не из запроса напрямую.
    sort_field = SORT_FIELDS.get(sort, "date")
    concerts_qs = concerts_qs.order_by(sort_field, "pk")

    # Пагинация применяется после фильтрации и сортировки.
    paginator = Paginator(concerts_qs, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "concerts": page_obj,
        "page_obj": page_obj,
        "today": date.today(),
        "query": query,
        "selected_venue": venue_id,
        "selected_performer": performer_id,
        "selected_status": status,
        "date_from": date_from,
        "sort": sort,
        "venues": Venue.objects.order_by("name"),
        "performers": Performer.objects.order_by("name"),
        "status_choices": [
            ("", "Все концерты"),
            ("active", "Активные"),
            ("cancelled", "Отменённые"),
        ],
        "total_count": paginator.count,
        "error": error,
    }
    return render(request, "concerts/concert_list.html", context)


def concert_detail(request: HttpRequest, concert_id: int):
    """Показать концерт и связанные объекты, рассчитанные в модели."""
    concert = get_object_or_404(
        Concert.objects.select_related(
            "performer", "venue", "program"
        ),
        pk=concert_id,
    )
    today = date.today()
    context = {
        "concert": concert,
        "today": today,
        "status": concert.get_status(today),
        "ticket_price": concert.calculate_ticket_price(),
        "revenue": concert.calculate_revenue(),
        "venue_fit": concert.check_venue_fit(),
    }
    return render(request, "concerts/concert_detail.html", context)


def statistics(request: HttpRequest):
    """Показать статистику: агрегаты, группировки и аннотации ORM."""
    today = date.today()

    # Сводные показатели по всем концертам.
    overall = Concert.objects.aggregate(
        total=Count("pk"),
        guests=Sum("expected_guests"),
        min_price=Min("base_ticket_price"),
        max_price=Max("base_ticket_price"),
        avg_price=Avg("base_ticket_price"),
    )

    # Группировка по признаку отмены через values() и annotate().
    by_status = (
        Concert.objects.values("is_cancelled")
        .annotate(count=Count("pk"), guests=Sum("expected_guests"))
        .order_by("is_cancelled")
    )

    # Статистика по площадкам: все площадки, включая пустые.
    venue_stats = (
        Venue.objects.annotate(
            total_count=Count("concerts"),
            active_count=Count(
                "concerts",
                filter=Q(concerts__is_cancelled=False),
            ),
            guests=Sum(
                "concerts__expected_guests",
                filter=Q(concerts__is_cancelled=False),
            ),
        )
        .order_by("-total_count", "name")
    )

    # Пять исполнителей с наибольшим числом концертов.
    performer_stats = (
        Performer.objects.annotate(
            concerts_count=Count("concerts"),
            avg_guests=Avg("concerts__expected_guests"),
        )
        .filter(concerts_count__gt=0)
        .order_by("-concerts_count", "name")[:5]
    )

    upcoming = Concert.objects.filter(
        date__gte=today,
        is_cancelled=False,
    ).count()

    context = {
        "today": today,
        "overall": overall,
        "by_status": by_status,
        "venue_stats": venue_stats,
        "performer_stats": performer_stats,
        "upcoming": upcoming,
    }
    return render(request, "concerts/statistics.html", context)
