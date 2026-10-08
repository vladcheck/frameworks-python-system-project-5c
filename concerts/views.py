from datetime import date

from django.http import HttpRequest
from django.shortcuts import render

from src.models.concerts import get_concert_by_id
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
    return concerts


def concerts(request: HttpRequest):
    concerts_list = _load_all()
    today = date.today()
    return render(
        request,
        "concerts/concert_list.html",
        {"concerts": concerts_list, "today": today},
    )


def concert_detail(request: HttpRequest, concert_id: int):
    concerts_list = _load_all()
    concert = get_concert_by_id(concerts_list, concert_id)
    today = date.today()
    if concert is None:
        context = {"concert": None, "today": today}
    else:
        status = concert.get_status(today)
        ticket_price = concert.calculate_ticket_price()
        revenue = concert.calculate_revenue()
        venue_fit = concert.check_venue_fit()
        context = {
            "concert": concert,
            "today": today,
            "status": status,
            "ticket_price": ticket_price,
            "revenue": revenue,
            "venue_fit": venue_fit,
        }
    return render(
        request,
        "concerts/concert_detail.html",
        context,
        status=404 if concert is None else 200,
    )
