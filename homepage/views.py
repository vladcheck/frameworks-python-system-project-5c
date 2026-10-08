from django.http import HttpResponse
from django.shortcuts import render


def page(title: str, content: str) -> str:
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
    )
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-
scale=1">
    <title>{title}</title>
    <link rel="stylesheet" href="{bootstrap}">
</head>
<body>
    <nav class="nav">
        <a class="nav-link" href="/">Главная</a>
        <a class="nav-link" href="/venues/">Концертные площадки</a>
        <a class="nav-link" href="/performers/">Исполнители</a>
        <a class="nav-link" href="/programs/">Программы</a>
        <a class="nav-link" href="/concerts/">Концерты</a>
    </nav>
    <main class="container">{content}</main>
</body>
</html>"""


def page_not_found(request, exception):
    return render(request, "404.html", status=404)


def index(request):
    return render(request, "homepage/index.html")
