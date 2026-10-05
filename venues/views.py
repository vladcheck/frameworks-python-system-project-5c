from django.http import HttpRequest, HttpResponse


def venues(request: HttpRequest):
    return HttpResponse("Список концертных площадок")


def venue_detail(request: HttpRequest, venue_id: int):
    return HttpResponse(f"Концертная площадка {venue_id}")
