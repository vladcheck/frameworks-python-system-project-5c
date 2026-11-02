"""Представления приложения performers: ORM-запросы и связи моделей."""

from django.db.models import Avg, Count, Q, Sum
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from .models import Performer


def performers(request: HttpRequest):
    """Показать список исполнителей с поиском и числом концертов."""
    query = request.GET.get("q", "").strip()

    # annotate() считает связанные концерты, Count() группирует записи.
    performers_qs = Performer.objects.annotate(
        concert_count=Count("concerts"),
    )
    if query:
        # Поиск сразу по двум полям модели через Q().
        performers_qs = performers_qs.filter(
            Q(name__icontains=query) | Q(genre__icontains=query)
        )
    performers_qs = performers_qs.order_by("-rating", "name")

    context = {
        "performers": performers_qs,
        "query": query,
        "total_count": performers_qs.count(),
    }
    return render(request, "performers/performer_list.html", context)


def performer_detail(request: HttpRequest, performer_id: int):
    """Показать исполнителя и связанные концерты через обратную связь."""
    performer = get_object_or_404(Performer, pk=performer_id)

    # Обратная связь related_name="concerts" и select_related().
    related = performer.concerts.select_related(
        "venue", "program"
    ).order_by("date")

    # Агрегирование по связанным концертам исполнителя.
    totals = performer.concerts.aggregate(
        total_guests=Sum("expected_guests"),
        avg_price=Avg("base_ticket_price"),
    )

    context = {
        "performer": performer,
        "related": related,
        "totals": totals,
    }
    return render(request, "performers/performer_detail.html", context)
