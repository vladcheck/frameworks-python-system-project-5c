"""Представления приложения concerts: ORM, формы, фильтры, пагинация."""

from datetime import date

from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Min, Q, Sum
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from performers.models import Performer
from venues.models import Venue

from .forms import ConcertFilterForm, ConcertForm
from .models import Concert

# Белый список параметров сортировки: URL -> поле модели.
SORT_FIELDS = {
    "date": "date",
    "title": "title",
    "venue": "venue__name",
    "performer": "performer__name",
}

# Белый список фильтров по статусу концерта: URL -> константа модели.
STATUS_FILTERS = {
    "active": Concert.Status.SCHEDULED,
    "cancelled": Concert.Status.CANCELLED,
}

PAGE_SIZE = 6


def concerts(request: HttpRequest):
    """Показать список концертов с поиском, фильтрами, сортировкой и страницами."""
    form = ConcertFilterForm(request.GET or None)
    # Однократная валидация: значения берутся только из cleaned_data.
    form_valid = form.is_bound and form.is_valid()
    error = None

    # select_related() загружает связанные объекты одним запросом.
    concerts_qs = Concert.objects.select_related(
        "performer", "venue", "program"
    )

    if form_valid:
        query = form.cleaned_data.get("q") or ""
        venue = form.cleaned_data.get("venue")
        performer = form.cleaned_data.get("performer")
        status = form.cleaned_data.get("status") or ""
        date_from = form.cleaned_data.get("date_from")
        sort = form.cleaned_data.get("sort") or "date"

        if query:
            # Поиск по названию концерта и по имени связанного исполнителя.
            concerts_qs = concerts_qs.filter(
                Q(title__icontains=query) | Q(performer__name__icontains=query)
            )
        if venue is not None:
            # Фильтрация по полю связанной модели (внешний ключ).
            concerts_qs = concerts_qs.filter(venue=venue)
        if performer is not None:
            concerts_qs = concerts_qs.filter(performer=performer)
        if status in STATUS_FILTERS:
            concerts_qs = concerts_qs.filter(status=STATUS_FILTERS[status])
        if date_from is not None:
            concerts_qs = concerts_qs.filter(date__gte=date_from)
    else:
        query = ""
        venue = None
        performer = None
        status = ""
        date_from = None
        sort = "date"
        if form.is_bound:
            # Форма отправлена, но не прошла валидацию.
            error = "Проверьте введённые значения фильтров."

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
        "selected_venue": venue.pk if venue is not None else "",
        "selected_performer": performer.pk if performer is not None else "",
        "selected_status": status,
        "date_from": date_from.isoformat() if date_from is not None else "",
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
        "form": form,
    }
    return render(request, "concerts/concert_list.html", context)


def concert_create(request: HttpRequest):
    """Создать новый концерт: форма с проверкой занятости площадки."""
    if request.method == "POST":
        form = ConcertForm(request.POST)
        if form.is_valid():
            concert = form.save(commit=False)
            occupied = Concert.objects.scheduled().filter(
                venue=concert.venue,
                date=concert.date,
            ).exists()
            if occupied:
                form.add_error(
                    None,
                    "Выбранная площадка уже занята на эту дату.",
                )
            else:
                form.save()
                return redirect("concerts:concerts")
    else:
        # Новый концерт по умолчанию планируется на сегодня.
        form = ConcertForm(initial={"date": timezone.localdate()})
    return render(
        request,
        "concerts/concert_form.html",
        {"form": form},
    )


def concert_update(request: HttpRequest, concert_id: int):
    """Отредактировать запланированный концерт (404 для остальных статусов)."""
    concert = get_object_or_404(
        Concert.objects.scheduled(),
        pk=concert_id,
    )
    if request.method == "POST":
        form = ConcertForm(request.POST, instance=concert)
        if form.is_valid():
            updated = form.save(commit=False)
            occupied = (
                Concert.objects.scheduled()
                .filter(venue=updated.venue, date=updated.date)
                .exclude(pk=concert.pk)
                .exists()
            )
            if occupied:
                form.add_error(
                    None,
                    "Выбранная площадка уже занята на эту дату.",
                )
            else:
                form.save()
                return redirect("concerts:concerts")
    else:
        form = ConcertForm(instance=concert)
    return render(
        request,
        "concerts/concert_form.html",
        {"form": form, "concert": concert},
    )


@require_POST
def concert_cancel(request: HttpRequest, concert_id: int):
    """Отменить запланированный концерт (только POST-запрос)."""
    concert = get_object_or_404(
        Concert.objects.scheduled(),
        pk=concert_id,
    )
    concert.cancel()
    return redirect("concerts:concerts")


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
        "status": concert.get_status_display(),
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

    # Число концертов каждого статуса через Count с условиями Q.
    status_counts = Concert.objects.aggregate(
        scheduled=Count("pk", filter=Q(status=Concert.Status.SCHEDULED)),
        cancelled=Count("pk", filter=Q(status=Concert.Status.CANCELLED)),
        completed=Count("pk", filter=Q(status=Concert.Status.COMPLETED)),
    )

    # Группировка по статусу через values() и annotate().
    by_status = (
        Concert.objects.values("status")
        .annotate(count=Count("pk"), guests=Sum("expected_guests"))
        .order_by("status")
    )

    # Статистика по площадкам: все площадки, включая пустые.
    venue_stats = (
        Venue.objects.annotate(
            total_count=Count("concerts"),
            active_count=Count(
                "concerts",
                filter=Q(concerts__status=Concert.Status.SCHEDULED),
            ),
            guests=Sum(
                "concerts__expected_guests",
                filter=Q(concerts__status=Concert.Status.SCHEDULED),
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
        status=Concert.Status.SCHEDULED,
    ).count()

    context = {
        "today": today,
        "overall": overall,
        "status_counts": status_counts,
        "by_status": by_status,
        "venue_stats": venue_stats,
        "performer_stats": performer_stats,
        "upcoming": upcoming,
    }
    return render(request, "concerts/statistics.html", context)
