from django.http import HttpResponse


def index(request):
    return HttpResponse("Concerty - система учета концертных выступлений")
