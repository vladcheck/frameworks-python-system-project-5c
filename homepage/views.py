from django.http import HttpResponse


def page(title: str, content: str) -> str:
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
        "/dist/css/bootstrap.min.css"
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
    content = """
    <h1 class="text-danger">404 – страница не найдена</h1>
    <p>Проверьте адрес или вернитесь на главную.</p>
    <a href="/" class="btn btn-primary">На главную</a>
    """
    return HttpResponse(
        page("404 – страница не найдена", content),
        status=404,
    )


def index(request):
    content = """
    <h1 class="display-4">Concerty</h1>
    <p class="lead">Система бронирования концертных помещений.</p>
    <p>Основные разделы:</p>
    <a href="/venues/" class="btn btn-primary me-2">Концертные площадки</a>
    <a href="/performers/" class="btn btn-primary me-2">Исполнители</a>
    <a href="/programs/" class="btn btn-primary me-2">Программы</a>
    <a href="/concerts/" class="btn btn-primary me-2">Концерты</a>
    """
    return HttpResponse(page("Concerty", content))
