from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, "404.html", status=404)


def index(request):
    return render(request, "homepage/index.html")
