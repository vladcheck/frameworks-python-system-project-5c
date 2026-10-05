from django.http import HttpRequest, HttpResponse


def performers(request: HttpRequest):
    return HttpResponse("Список выступающих")


def performer_detail(request: HttpRequest, performer_id: int):
    return HttpResponse(f"Выступающий {performer_id}")
