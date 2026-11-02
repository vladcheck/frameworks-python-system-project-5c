"""Отчёт ПР9: модели Django, связи и операции с базой данных через ORM.

Структура по методичке, раздел 7.4: цель, материалы Практикума,
доработка проекта, результат, проверка, Git, вывод, источники.
"""
from gost_report import MIREA_PROFILE, Report, TitleConfig

r = Report(
    TitleConfig(
        work_type="Практическая работа",
        work_number="№9",
        topic="Модели Django, связи и операции с базой данных через ORM",
        student_name="Валекжанин Владимир Сергеевич",
        student_group="ЭФБО-04-24",
        year="2026",
        discipline="Технологии разработки приложений на базе фреймворков",
        department="Кафедра индустриального программирования",
        faculty="Институт перспективных технологий и индустриального программирования",
    ),
    profile=MIREA_PROFILE,
)

r.bib.add(
    "praktikum-backend",
    type="web",
    authors=["Яндекс Практикум"],
    title="Бэкенд-разработка",
    url="https://practicum.yandex.ru/backend-developer/",
    accessed="01.11.2026",
)
r.bib.add(
    "django-models",
    type="web",
    authors=["Django Software Foundation"],
    title="Models",
    url="https://docs.djangoproject.com/en/5.2/topics/db/models/",
    accessed="01.11.2026",
)
r.bib.add(
    "django-many-to-one",
    type="web",
    authors=["Django Software Foundation"],
    title="Many-to-one relationships",
    url="https://docs.djangoproject.com/en/5.2/topics/db/examples/many_to_one/",
    accessed="01.11.2026",
)
r.bib.add(
    "django-migrations",
    type="web",
    authors=["Django Software Foundation"],
    title="Migrations",
    url="https://docs.djangoproject.com/en/5.2/topics/migrations/",
    accessed="01.11.2026",
)
r.bib.add(
    "python-sqlite3",
    type="web",
    authors=["Python Software Foundation"],
    title="sqlite3, интерфейс DB-API 2.0 для баз данных SQLite",
    url="https://docs.python.org/3/library/sqlite3.html",
    accessed="01.11.2026",
)
r.bib.add(
    "django-queries",
    type="web",
    authors=["Django Software Foundation"],
    title="Making queries",
    url="https://docs.djangoproject.com/en/5.2/topics/db/queries/",
    accessed="01.11.2026",
)

r.toc_static([
    (1, "Введение", 4),
    (1, "1 Материалы Яндекс Практикума", 5),
    (1, "2 Доработка проекта", 6),
    (1, "3 Результат работы и проверка", 8),
    (1, "Вывод", 10),
    (1, "Список использованных источников", 11),
])

r.h1("Введение", center=True)
r.text(
    "Цель работы перевести индивидуальный проект Concerty на Django ORM: "
    "описать модели сущностей и их поля, настроить связи между моделями, "
    "создать и применить миграции, перенести данные базы ПР7 без потери связей "
    "и заменить прямые SQL-запросы операциями ORM. Материалы раздела 05 курса "
    "«Бэкенд-разработка» дают базовые приёмы работы с моделями и запросами "
    + r.bib.cite("praktikum-backend")
    + "."
)

r.h1("1 Материалы Яндекс Практикума")
r.text(
    "Выполнены материалы раздела 05 «База данных и Django ORM» курса "
    "«Бэкенд-разработка». Перечень тем и отметки о выполнении приведены ниже."
)
t1 = r.table(
    [
        ["Тема", "Отметка о выполнении"],
        ["Отношения между таблицами", "Выполнено"],
        ["Связь один-к-одному", "Выполнено"],
        ["Связь многие-к-одному", "Выполнено"],
        ["Соединение таблиц JOIN", "Выполнено"],
        ["Связь многие-ко-многим", "Выполнено"],
        ["Ссылочная целостность", "Выполнено"],
        ["Описание таблиц классами моделей", "Выполнено"],
        ["Связи моделей", "Выполнено"],
        ["Абстрактные модели", "Выполнено"],
        ["Миграции", "Выполнено"],
        ["CRUD-операции в Django shell", "Выполнено"],
        ["Команды dumpdata и loaddata", "Выполнено"],
    ],
    caption="Материалы раздела 05 курса «Бэкенд-разработка»",
)
r.text(
    "Все двенадцать тем "
    + r.ref.in_table(t1)
    + " отмечены как выполненные, приёмы раздела повторены в проекте."
)

r.h1("2 Доработка проекта")

r.h2("2.1 Модели и связи")
r.text(
    "Слой данных переведён на ORM в приложениях performers, venues, programs "
    "и concerts. Каждая сущность описана классом Django, поля получили подписи "
    "verbose_name. Модель Concert связывает исполнителя, площадку и программу "
    "тремя внешними ключами."
)
t2 = r.table(
    [
        ["Модель", "Поля", "Связи и методы"],
        ["Performer", "name, genre, rating", "Обратная связь concerts"],
        ["Venue", "name, city, capacity", "Обратная связь concerts, is_suitable_for"],
        ["Program", "name, duration, age_limit", "Обратная связь concerts, is_allowed_for"],
        [
            "Concert",
            "title, date, expected_guests, base_ticket_price, is_cancelled",
            "Три внешних ключа с PROTECT",
        ],
    ],
    caption="Модели проекта и их поля",
)
r.text(
    "Состав моделей приведён "
    + r.ref.in_table(t2)
    + ". У модели Concert есть методы get_status, calculate_ticket_price, "
    "check_venue_fit, calculate_revenue и cancel. У всех моделей задан Meta "
    "ordering: исполнители, площадки и программы сортируются по названию, "
    "концерты по дате и идентификатору. Связи описаны по документации Django "
    + r.bib.cite("django-models", "django-many-to-one")
    + "."
)
r.text(
    "Параметр on_delete со значением PROTECT запрещает удаление исполнителя, "
    "площадки или программы, пока на них ссылается концерт. Модели "
    "зарегистрированы в административной панели с list_display, list_filter, "
    "search_fields и list_select_related."
)

r.h2("2.2 Миграции и перенос данных")
r.text(
    "Для каждого приложения создана начальная миграция 0001_initial: performers, "
    "venues, programs и concerts. Миграция concerts зависит от трёх остальных "
    "из-за внешних ключей. Порядок миграций описан в документации Django "
    + r.bib.cite("django-migrations")
    + ". Миграции применены к db.sqlite3."
)
r.text(
    "Выбранная стратегия: таблицами управляют миграции Django, а данные читаются "
    "из базы ПР7 data/concerty.sqlite только на чтение. Перенос выполняет "
    "db/import_sqlite_to_orm.py: записи создаются через "
    "update_or_create в одной транзакции transaction.atomic, исходные "
    "идентификаторы сохраняются, даты и суммы преобразуются через "
    "date.fromisoformat и Decimal "
    + r.bib.cite("python-sqlite3")
    + ". Сначала переносятся справочники, затем concerts. Перенесено "
    "12 исполнителей, 12 площадок, 12 программ и 15 концертов."
)

r.h2("2.3 Операции ORM и страницы")
r.text(
    "Представления четырёх приложений переведены на ORM и используют более "
    "пятнадцати видов ORM-выражений: objects.all() и order_by по нескольким "
    "полям и связанным полям; get_object_or_404 с select_related; filter по "
    "одному и нескольким условиям, по дате date__gte и внешнему ключу; exclude "
    "с pk__in; поиск на Q с icontains; values и values_list; annotate с Count и "
    "Sum; aggregate с Count, Sum, Avg, Min и Max; группировка values с annotate; "
    "обратные связи; срез [:5] и Paginator. Список концертов получил поиск по "
    "названию и исполнителю, фильтры по площадке, исполнителю, статусу и дате "
    "начала, сортировку по белому списку и пагинацию по шесть записей. Добавлены "
    "страницы статистики /concerts/statistics/ и подбора площадок "
    "/venues/available/. Шаблоны обновлены, README.md описывает модели, "
    "миграции, перенос данных и проверки. Запросы построены по документации "
    "Django "
    + r.bib.cite("django-queries")
    + "."
)

r.h1("3 Результат работы и проверка")

r.h2("3.1 Результат работы")
r.numbered([
    "Описаны модели Performer, Venue, Program и Concert с полями и методами.",
    "Настроены связи многие-к-одному через внешние ключи с PROTECT и related_name.",
    "Созданы и применены миграции 0001_initial во всех приложениях.",
    "Данные перенесены из базы ПР7 без потери связей, идентификаторы сохранены.",
    "Операции с данными выполняются средствами ORM, прямые SQL-запросы из "
    "представлений убраны.",
    "Страницы и пользовательские сценарии работают без изменений, добавлены "
    "статистика и подбор площадок.",
])

r.h2("3.2 Проверка")
r.text("Команды проверки запущены из корня проекта, их результаты приведены ниже.")
t3 = r.table(
    [
        ["Команда", "Результат"],
        ["python manage.py check", "Ошибок не обнаружено"],
        [
            "python manage.py showmigrations",
            "Отметка [X] у миграций 0001_initial в четырёх приложениях",
        ],
        ["python manage.py makemigrations --check", "No changes detected"],
        ["pytest -q", "215 passed"],
        ["flake8 . --extend-exclude=venv", "Замечаний нет"],
    ],
    caption="Результаты проверок проекта",
)
r.text(
    "Все проверки "
    + r.ref.in_table(t3)
    + " проходят без ошибок. Набор тестов включает 130 старых тестов, 32 теста "
    "представлений и 53 теста ORM."
)

r.h2("3.3 Git")
r.text(
    "Работа выполнена в ветке main. Изменения ПР9 зафиксированы семью коммитами."
)
t4 = r.table(
    [
        ["Коммит", "Сообщение"],
        ["f9af930", "исходное состояние проекта перед переходом на ORM"],
        ["ae2df9b", "модели Django, связи и миграции"],
        ["8872dab", "представления переведены на ORM"],
        ["69aa69b", "тесты моделей, ORM-запросов и представлений"],
        ["7bd63c0", "README и настройки проверки кода"],
        ["5741aa5", "порядок восстановления данных ПР7"],
        ["8f9c1d9", "описание истории коммитов в README"],
    ],
    caption="Коммиты ПР9 в ветке main",
)
r.text(
    "Список коммитов приведён "
    + r.ref.in_table(t4)
    + ". Файлы отчёта добавляются отдельным коммитом после сборки."
)

r.h1("Вывод", center=True)
r.text(
    "Проект переведён на Django ORM: модели описывают сущности и связи, схема "
    "базы управляется миграциями, данные ПР7 перенесены с сохранением связей. "
    "Представления и шаблоны работают через ORM, добавлены страницы статистики и "
    "подбора площадок. Прямые SQL-запросы остаются в репозитории как реализация "
    "ПР7, но в пользовательских сценариях не используются."
)

r.bib.references()

out = r.save("ПР9_Отчет.docx")
print(f"Wrote {out}")