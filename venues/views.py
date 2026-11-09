"""Представления приложения venues: ORM, фильтры и доступность."""

from datetime import date, datetime

from django.db.models import Count, Q
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from concerts.models import Concert

from .models import Venue


def _parse_date(value: str):
    """Преобразовать строку ГГГГ-ММ-ДД в объект date или вернуть None."""
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def venues(request: HttpRequest):
    """Показать список площадок с поиском и отбором по вместимости."""
    query = request.GET.get("q", "").strip()
    min_capacity = request.GET.get("min_capacity", "").strip()

    # annotate() добавляет число концертов каждой площадки.
    venues_qs = Venue.objects.annotate(concert_count=Count("concerts"))
    if query:
        venues_qs = venues_qs.filter(
            Q(name__icontains=query) | Q(city__icontains=query)
        )
    if min_capacity.isdigit():
        venues_qs = venues_qs.filter(capacity__gte=int(min_capacity))
    venues_qs = venues_qs.order_by("-capacity", "name")

    context = {
        "venues": venues_qs,
        "query": query,
        "min_capacity": min_capacity,
        "total_count": venues_qs.count(),
    }
    return render(request, "venues/venue_list.html", context)


def venue_detail(request: HttpRequest, slug: str):
    """Показать площадку, её концерты и доступность на текущую дату."""
    venue = get_object_or_404(Venue, slug=slug)

    # Связанные концерты через обратную связь и select_related().
    related = venue.concerts.select_related(
        "performer", "program"
    ).order_by("date")

    # Отменённые и завершённые концерты площадку не блокируют.
    busy_today = venue.concerts.filter(
        date=date.today(),
        status=Concert.Status.SCHEDULED,
    ).exists()

    context = {
        "venue": venue,
        "related": related,
        "available": not busy_today,
        "status_text": "занята" if busy_today else "свободна",
    }
    return render(request, "venues/venue_detail.html", context)


def available_venues(request: HttpRequest):
    """Найти площадки, свободные на выбранную дату (exclude())."""
    booking_date = request.GET.get("date", "").strip()
    venues_list = Venue.objects.none()
    error = None

    if booking_date:
        selected_date = _parse_date(booking_date)
        if selected_date is None:
            error = "Укажите корректную дату."
        else:
            # Идентификаторы площадок с запланированными концертами на дату.
            booked_venue_ids = Concert.objects.filter(
                date=selected_date,
                status=Concert.Status.SCHEDULED,
            ).values_list("venue_id", flat=True)
            # exclude() убирает занятые площадки из общего списка.
            venues_list = Venue.objects.exclude(
                pk__in=booked_venue_ids,
            ).order_by("name")

    context = {
        "venues": venues_list,
        "booking_date": booking_date,
        "error": error,
    }
    return render(request, "venues/available.html", context)
