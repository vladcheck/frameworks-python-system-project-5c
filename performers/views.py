from django.http import HttpRequest, HttpResponse

from homepage.views import page
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
    items = ""
    for performer in performers_list:
        text = f"{performer.name} ({performer.genre}) — рейтинг {performer.rating}"
        items += (
            f'<li class="list-group-item">'
            f'<a href="/performers/{performer.id}/">{text}</a></li>'
        )
    content = f"""
    <h1>Исполнители</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Concerty — исполнители", content))


def performer_detail(request: HttpRequest, performer_id: int):
    performers_list, concerts_list = _load_all()
    performer = get_performer_by_id(performers_list, performer_id)
    if performer is None:
        content = """
        <h1 class="text-danger">Исполнитель не найден</h1>
        <a href="/performers/" class="btn btn-outline-secondary">
            ← к списку исполнителей
        </a>
        """
        return HttpResponse(
            page("Исполнитель не найден", content),
            status=404,
        )
    related = [c for c in concerts_list if c.performer.id == performer.id]
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
            <h5 class="card-title">{performer.name}</h5>
            <p class="card-text">
                <strong>ID:</strong> {performer.id}
            </p>
            <p class="card-text">
                <strong>Жанр:</strong> {performer.genre}
            </p>
            <p class="card-text">
                <strong>Рейтинг:</strong> {performer.rating}
            </p>
            <h6>Концерты исполнителя:</h6>
            <ul class="list-group mb-3">{rel_items}</ul>
            <a href="/performers/"
                class="btn btn-outline-secondary">
                ← к списку исполнителей
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(performer.name, content), status=200)
