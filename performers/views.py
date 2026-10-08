from django.http import HttpRequest
from django.shortcuts import render

from src.models.performers import get_performer_by_id
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
    return performers, concerts


def performers(request: HttpRequest):
    performers_list, _ = _load_all()
    return render(
        request,
        "performers/performer_list.html",
        {"performers": performers_list},
    )


def performer_detail(request: HttpRequest, performer_id: int):
    performers_list, concerts_list = _load_all()
    performer = get_performer_by_id(performers_list, performer_id)
    if performer is None:
        context = {"performer": None, "related": []}
    else:
        related = [c for c in concerts_list if c.performer.id == performer.id]
        context = {
            "performer": performer,
            "related": related,
        }
    return render(
        request,
        "performers/performer_detail.html",
        context,
        status=404 if performer is None else 200,
    )
