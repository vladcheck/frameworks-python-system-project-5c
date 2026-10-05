"""Тесты Django-представлений (списки, детали, 404) через test Client."""

import os

import django
from django.test import Client, override_settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "concerty.settings")
django.setup()

from django.conf import settings  # noqa: E402

if "testserver" not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, "testserver"]

client = Client()

LIST_PAGES = [
    "/concerts/",
    "/venues/",
    "/performers/",
    "/programs/",
]

DETAIL_PAGES = [
    ("/concerts/1/", "Клубный вечер с Мейби Бейби"),
    ("/venues/1/", "Adrenaline Stadium"),
    ("/performers/1/", "Мейби Бейби"),
    ("/programs/1/", "MAYDAY: клубный сет"),
]

MISSING_PAGES = [
    "/concerts/999/",
    "/venues/999/",
    "/performers/999/",
    "/programs/999/",
]


def test_index_ok():
    response = client.get("/")
    assert response.status_code == 200
    content = response.content.decode()
    for url in LIST_PAGES:
        assert f'href="{url}"' in content


def test_list_pages_ok():
    for url in LIST_PAGES:
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "<!DOCTYPE html>" in content
        assert 'href="/"' in content


def test_detail_pages_ok():
    for url, title in DETAIL_PAGES:
        response = client.get(url)
        assert response.status_code == 200
        assert title in response.content.decode()


def test_detail_back_links():
    pairs = [
        ("/concerts/1/", "/concerts/"),
        ("/venues/1/", "/venues/"),
        ("/performers/1/", "/performers/"),
        ("/programs/1/", "/programs/"),
    ]
    for detail_url, list_url in pairs:
        content = client.get(detail_url).content.decode()
        assert list_url in content


def test_missing_details_404():
    for url in MISSING_PAGES:
        assert client.get(url).status_code == 404


@override_settings(DEBUG=False)
def test_custom_404_page():
    response = client.get("/nonexistent/")
    assert response.status_code == 404
    content = response.content.decode()
    assert "страница не найдена" in content
    assert "404" in content
