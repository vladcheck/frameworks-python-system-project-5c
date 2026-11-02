from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, "404.html", status=404)


def index(request):
    return render(request, "homepage/index.html", {"xss_threat": """
        <script>
        document.body.textContent = "Вас взломали!"
        </script>
    """})  # pragma: no cover

    return render(request, "homepage/index.html")


def demo_escape(request):
    payload = '<script>alert("XSS")</script><b>жирный</b>'
    return render(request, "homepage/demo_escape.html", {"payload": payload})
