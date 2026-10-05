from django.http import HttpRequest, HttpResponse


def programs(request: HttpRequest):
    return HttpResponse("Список программ")


def program_detail(request: HttpRequest, program_id: int):
    return HttpResponse(f"Программа {program_id}")
