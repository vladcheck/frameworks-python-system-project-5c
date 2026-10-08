from django.http import HttpRequest
from django.shortcuts import render

from src.models.programs import get_program_by_id
from src.storage import (
    load_concerts,
    load_performers,
    load_programs,
    load_venues,
)


def _load_all():
    performers = load_performers("data/performers.json")
    venues = load_venues("data/venues.json")
    programs = load_programs("data/programs.json")
    concerts = load_concerts("data/concerts.json", performers, venues, programs)
    return programs, concerts


def programs(request: HttpRequest):
    programs_list, _ = _load_all()
    return render(
        request,
        "programs/program_list.html",
        {"programs": programs_list},
    )


def program_detail(request: HttpRequest, program_id: int):
    programs_list, concerts_list = _load_all()
    program = get_program_by_id(programs_list, program_id)
    if program is None:
        context = {"program": None, "related": []}
    else:
        related = [c for c in concerts_list if c.program.id == program.id]
        context = {
            "program": program,
            "related": related,
        }
    return render(
        request,
        "programs/program_detail.html",
        context,
        status=404 if program is None else 200,
    )
