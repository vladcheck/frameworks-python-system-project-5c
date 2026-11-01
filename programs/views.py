"""Представления приложения programs: ORM-запросы и связи моделей."""

from django.db.models import Count
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from .models import Program


def programs(request: HttpRequest):
    """Показать список программ с поиском и отбором по возрасту."""
    query = request.GET.get("q", "").strip()
    max_age = request.GET.get("max_age", "").strip()

    # annotate() добавляет число концертов с этой программой.
    programs_qs = Program.objects.annotate(
        concert_count=Count("concerts"),
    )
    if query:
        programs_qs = programs_qs.filter(name__icontains=query)
    if max_age.isdigit():
        programs_qs = programs_qs.filter(age_limit__lte=int(max_age))
    programs_qs = programs_qs.order_by("duration", "name")

    context = {
        "programs": programs_qs,
        "query": query,
        "max_age": max_age,
        "total_count": programs_qs.count(),
    }
    return render(request, "programs/program_list.html", context)


def program_detail(request: HttpRequest, program_id: int):
    """Показать программу и связанные концерты через обратную связь."""
    program = get_object_or_404(Program, pk=program_id)

    related = program.concerts.select_related(
        "performer", "venue"
    ).order_by("date")

    context = {
        "program": program,
        "related": related,
    }
    return render(request, "programs/program_detail.html", context)
