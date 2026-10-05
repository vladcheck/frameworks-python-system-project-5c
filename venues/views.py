from datetime import date

from django.http import HttpRequest, HttpResponse

from homepage.views import page
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
    items = ""
    for venue in venues_list:
        text = f"{venue.name}, {venue.city} — {venue.capacity} мест"
        items += (
            f'<li class="list-group-item"><a href="/venues/{venue.id}/">{text}</a></li>'
        )
    content = f"""
    <h1>Площадки</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Concerty — площадки", content))


def venue_detail(request: HttpRequest, venue_id: int):
    venues_list, concerts_list = _load_all()
    venue = get_venue_by_id(venues_list, venue_id)
    if venue is None:
        content = """
        <h1 class="text-danger">Площадка не найдена</h1>
        <a href="/venues/" class="btn btn-outline-secondary">
            ← к списку площадок
        </a>
        """
        return HttpResponse(
            page("Площадка не найдена", content),
            status=404,
        )
    available = is_venue_available(concerts_list, venue.id, date.today())
    status = "свободна" if available else "занята"
    badge = "bg-success" if available else "bg-danger"
    related = [c for c in concerts_list if c.venue.id == venue.id]
    rel_items = (
        "".join(
            f'<li class="list-group-item"><a href="/concerts/{c.id}/">'
            f"{c.title} — {c.date}</a></li>"
            for c in related
        )
        or '<li class="list-group-item">Нет концертов</li>'
    )
    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{venue.name}</h5>
            <p class="card-text">
                <strong>ID:</strong> {venue.id}
            </p>
            <p class="card-text">
                <strong>Город:</strong> {venue.city}
            </p>
            <p class="card-text">
                <strong>Вместимость:</strong> {venue.capacity} мест
            </p>
            <p class="card-text">
                Доступность на текущую дату:
                <span class="badge {badge}">{status}</span>
            </p>
            <h6>Концерты на площадке:</h6>
            <ul class="list-group mb-3">{rel_items}</ul>
            <a href="/venues/"
                class="btn btn-outline-secondary">
                ← к списку площадок
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(venue.name, content), status=200)
