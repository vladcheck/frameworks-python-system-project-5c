from django.http import HttpRequest, HttpResponse

from homepage.views import page
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
    items = ""
    for program in programs_list:
        text = f"{program.name} — {program.duration} мин, {program.age_limit}+"
        items += (
            f'<li class="list-group-item">'
            f'<a href="/programs/{program.id}/">{text}</a></li>'
        )
    content = f"""
    <h1>Программы</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Concerty — программы", content))


def program_detail(request: HttpRequest, program_id: int):
    programs_list, concerts_list = _load_all()
    program = get_program_by_id(programs_list, program_id)
    if program is None:
        content = """
        <h1 class="text-danger">Программа не найдена</h1>
        <a href="/programs/" class="btn btn-outline-secondary">
            ← к списку программ
        </a>
        """
        return HttpResponse(
            page("Программа не найдена", content),
            status=404,
        )
    related = [c for c in concerts_list if c.program.id == program.id]
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
            <h5 class="card-title">{program.name}</h5>
            <p class="card-text">
                <strong>ID:</strong> {program.id}
            </p>
            <p class="card-text">
                <strong>Продолжительность:</strong>
                {program.duration} мин
            </p>
            <p class="card-text">
                <strong>Возрастное ограничение:</strong>
                {program.age_limit}+
            </p>
            <h6>Концерты с программой:</h6>
            <ul class="list-group mb-3">{rel_items}</ul>
            <a href="/programs/"
                class="btn btn-outline-secondary">
                ← к списку программ
            </a>
        </div>
    </div>
    """
    return HttpResponse(page(program.name, content), status=200)
