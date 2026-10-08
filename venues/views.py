from datetime import date

from django.http import HttpRequest
from django.shortcuts import render

from src.models.concerts import is_venue_available
from src.models.venues import get_venue_by_id
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
    return venues, concerts


def venues(request: HttpRequest):
    venues_list, _ = _load_all()
    return render(
        request,
        "venues/venue_list.html",
        {"venues": venues_list},
    )


def venue_detail(request: HttpRequest, venue_id: int):
    venues_list, concerts_list = _load_all()
    venue = get_venue_by_id(venues_list, venue_id)
    if venue is None:
        context = {"venue": None, "related": []}
    else:
        available = is_venue_available(concerts_list, venue.id, date.today())
        status_text = "свободна" if available else "занята"
        related = [c for c in concerts_list if c.venue.id == venue.id]
        context = {
            "venue": venue,
            "available": available,
            "status_text": status_text,
            "related": related,
        }
    return render(
        request,
        "venues/venue_detail.html",
        context,
        status=404 if venue is None else 200,
    )
