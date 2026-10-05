from django.http import HttpRequest, HttpResponse


def concerts(request: HttpRequest):
    return HttpResponse("Список концертов")


def concert_detail(request: HttpRequest, concert_id: int):
    return HttpResponse(f"Концерт {concert_id}")
