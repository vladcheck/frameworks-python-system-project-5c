from datetime import date

from django.http import HttpRequest, HttpResponse

from homepage.views import page
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
    items = ""
    for concert in concerts_list:
        status = concert.get_status(today)
        badge = "bg-secondary" if concert.is_cancelled else "bg-success"
        items += (
            '<li class="list-group-item '
            'd-flex justify-content-between">'
            f'<a href="/concerts/{concert.id}/">'
            f"{concert.title} — {concert.date}"
            "</a>"
            f'<span class="badge {badge}">{status}</span>'
            "</li>"
        )
    content = f"""
    <h1>Концерты</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Concerty — концерты", content))


def concert_detail(request: HttpRequest, concert_id: int):
    concerts_list = _load_all()
    concert = get_concert_by_id(concerts_list, concert_id)
    if concert is None:
        content = """
        <h1 class="text-danger">Концерт не найден</h1>
        <a href="/concerts/" class="btn btn-outline-secondary">
            ← к списку концертов
        </a>
        """
        return HttpResponse(
            page("Концерт не найден", content),
            status=404,
        )
    today = date.today()
    status = concert.get_status(today)
    badge = "bg-secondary" if concert.is_cancelled else "bg-success"
    ticket_price = concert.calculate_ticket_price()
    revenue = concert.calculate_revenue()
    venue_fit = concert.check_venue_fit()
    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">{concert.title}</h5>
            <p class="card-text">
                <strong>ID:</strong> {concert.id}
            </p>
            <p class="card-text">
                Исполнитель: {concert.performer.name}
                ({concert.performer.genre})
            </p>
            <p class="card-text">
                Площадка: {concert.venue.name}, {concert.venue.city}
            </p>
            <p class="card-text">
                Программа: {concert.program.name}
                ({concert.program.duration} мин,
                {concert.program.age_limit}+)
            </p>
            <p class="card-text">
                Дата: {concert.date}
            </p>
            <p class="card-text">
                Ожидается: {concert.expected_guests} зрителей
            </p>
            <p class="card-text">
                Цена билета: {ticket_price} руб.
            </p>
            <p class="card-text">
                Ожидаемая выручка: {revenue} руб.
            </p>
            <p class="card-text">{venue_fit}</p>
            <p class="card-text">
                Статус:
                <span class="badge {badge}">{status}</span>
            </p>
            <a href="/concerts/"
                class="btn btn-outline-secondary">
                ← к списку концертов
            </a>
        </div>
    </div>
    """
    return HttpResponse(
        page(concert.title, content),
        status=200,
    )
