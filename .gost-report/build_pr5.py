"""Отчёт ПР5: Django, HTTP и основы веб-разработки.

Структура по методичке, раздел 7.4: общие сведения, материалы Практикума,
доработка проекта, результат, вывод. Объём 1-2 страницы без титула.
"""
from gost_report import MIREA_PROFILE, Report, TitleConfig

r = Report(
    TitleConfig(
        work_type="Практическая работа",
        work_number="№5",
        topic="Django, HTTP и основы веб-разработки",
        student_name="Валекжанин Владимир Сергеевич",
        student_group="ЭФБО-04-24",
        year="2026",
        discipline="Технологии разработки приложений на базе фреймворков",
        department="Кафедра индустриального программирования",
        faculty="Институт перспективных технологий и индустриального программирования",
    ),
    profile=MIREA_PROFILE,
)

r.toc_static([
    (1, "Введение", 4),
    (1, "1 Материалы Яндекс Практикума", 5),
    (1, "2 Доработка проекта", 6),
    (1, "3 Результат работы", 7),
    (1, "Заключение", 8),
    (1, "Список использованных источников", 9),
])

r.h1("Введение", center=True)
r.text(
    "Цель работы изучить назначение фреймворка Django, структуру проекта и приложений, "
    "обработку HTTP запросов, маршрутизацию URL и основы веб страниц. Консольный проект "
    "Concerty из ПР3 переводится на начальный этап веб разработки: создаётся Django проект, "
    "приложения подключаются через маршрутизацию, страницы формируют view функции."
)

r.h1("1 Материалы Яндекс Практикума")
r.text(
    "Выполнены материалы раздела 04 «Основы веб-разработки» курса «Бэкенд-разработка»: "
    "создание проекта, пути и view-функции, вёрстка для бэкендера. Темы охватывают Django "
    "проект и приложения, протокол HTTP, конвертеры путей, HTML документ, CSS и Bootstrap."
)

r.h1("2 Доработка проекта")
r.text(
    "Проект «Система учета концертных выступлений» (Concerty): регистрация концертов, "
    "исполнителей, площадок и программ, контроль доступности площадок и статистика. "
    "Создан Django проект concerty, подключены приложения homepage, concerts, venues, "
    "performers и programs. Корневой urls.py разводит адреса через include, динамика через "
    "конвертер, каждая view функция готовит данные для ответа."
)
lst = r.listing(
    "path('concerts/', include('concerts.urls'))",
    "Подключение приложения через include",
)
r.text(
    f"Реализованы десять страниц: главная, списки и детали концертов, площадок, "
    f"исполнителей и программ {r.ref.on_listing(lst)}. Обработчик handler404 отдаёт страницу "
    "404 для неизвестных адресов. Модель ПР3 сохранена: данные грузятся из JSON каталога data, "
    "идентификаторы разрешаются в объекты Performer, Venue, Program и Concert. README обновлён, "
    "исходники лежат в репозитории https://github.com/vladcheck/frameworks-python-system-project-5c."
)

r.h1("3 Результат работы")
r.numbered([
    "Созданы Django приложения homepage, concerts, venues, performers и programs.",
    "Настроена двухуровневая маршрутизация с динамическими URL и страницей 404.",
    "Реализованы view-функции списков и деталей всех сущностей с навигацией.",
    "Сохранены предметная область ПР3, классы, JSON хранилище и консольная версия.",
])

r.h1("Заключение", center=True)
r.text(
    "Работа выполнена: изучены структура Django и цикл запрос ответ, настроена маршрутизация, "
    "реализованы view-функции и страницы. Проект готов к переносу на Django шаблоны."
)

r.bib.add(
    "django-docs",
    type="web",
    authors=["Django Software Foundation"],
    title="Django documentation",
    url="https://docs.djangoproject.com/en/5.2/",
    accessed="10.10.2026",
)
r.bib.add(
    "praktikum-backend",
    type="web",
    authors=["Яндекс Практикум"],
    title="Бэкенд-разработка",
    url="https://practicum.yandex.ru/backend-developer/",
    accessed="05.10.2026",
)
r.bib.add(
    "bootstrap-docs",
    type="web",
    authors=["Bootstrap"],
    title="Bootstrap documentation",
    url="https://getbootstrap.com/docs/5.3/",
    accessed="05.10.2026",
)
r.bib.add(
    "mozilla-http",
    type="web",
    authors=["MDN Web Docs"],
    title="Руководство по HTTP",
    url="https://developer.mozilla.org/ru/docs/Web/HTTP",
    accessed="05.10.2026",
)
r.bib.add(
    "mozilla-html",
    type="web",
    authors=["MDN Web Docs"],
    title="Руководство по HTML",
    url="https://developer.mozilla.org/ru/docs/Web/HTML",
    accessed="05.10.2026",
)
r.text(
    "Документация Django "
    + r.bib.cite("django-docs")
    + ", курс Практикума "
    + r.bib.cite("praktikum-backend")
    + ", оформление по "
    + r.bib.cite("bootstrap-docs")
    + ", HTTP и HTML по "
    + r.bib.cite("mozilla-http")
    + " и "
    + r.bib.cite("mozilla-html")
    + "."
)
r.bib.references()

out = r.save("ПР5_Отчет.docx")
print(f"Wrote {out}")
