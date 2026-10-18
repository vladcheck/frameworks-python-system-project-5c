"""Отчёт ПР7: Основы баз данных и SQL.

Структура по методичке, раздел 7.5: общие сведения, цель, материалы Практикума,
доработка проекта, результат, проверка, Git, вывод. Объём 1-2 страницы без титула.
"""
from gost_report import MIREA_PROFILE, Report, TitleConfig

r = Report(
    TitleConfig(
        work_type="Практическая работа",
        work_number="№7",
        topic="Основы баз данных и SQL",
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
    (1, "4 Проверка", 8),
    (1, "Заключение", 9),
    (1, "Список использованных источников", 10),
])

r.h1("Введение", center=True)
r.text(
    "Цель работы изучить основы реляционных баз данных и языка SQL на примере проекта "
    "Concerty: спроектировать таблицы, задать первичные и внешние ключи, освоить выборку, "
    "фильтрацию, сортировку, агрегаты и группировку в SQLite, перенести данные из JSON "
    "в базу и читать их из Python через sqlite3."
)

r.h1("1 Материалы Яндекс Практикума")
r.text(
    "Выполнены материалы раздела 05 курса «Бэкенд-разработка»: реляционные базы данных, "
    "язык SQL, первые запросы, работа с базой из Python, сортировка и LIMIT, агрегирующие "
    "функции и GROUP BY. Темы охватывают таблицы и ключи, SELECT с WHERE, ORDER BY, "
    "COUNT и SUM, группировку и работу через sqlite3."
)

r.h1("2 Доработка проекта")
r.text(
    "Схема sql/schema.sql задаёт четыре таблицы: performers, venues, programs и concerts. "
    "У каждой таблицы целочисленный первичный ключ id, концерты ссылаются на исполнителя, "
    "площадку и программу через внешние ключи performer_id, venue_id и program_id. "
    "Модуль db/database.py открывает соединение с data/concerty.sqlite и накатывает схему, "
    "скрипт db/import_json.py переносит данные из JSON каталога data в таблицы."
)
lst = r.listing(
    "conn = sqlite3.connect('data/concerty.sqlite')",
    "Подключение к базе SQLite из Python через sqlite3",
)
r.text(
    f"Файл sql/queries.sql содержит тринадцать запросов Q01 по Q13 {r.ref.on_listing(lst)}. "
    "Простые списки Q01 и Q02 сортируют исполнителей по рейтингу и площадки по вместимости, "
    "фильтры Q03, Q04 и Q05 отбирают площадки по вместимости и концерты по дате и статусу, "
    "запросы с JOIN Q06 и Q07 подставляют имена связанных сущностей, Q08 и Q09 проверяют "
    "свободу площадок на дату с учётом отмен, агрегаты Q10 и Q11 считают концерты и гостей, "
    "группировки Q12 и Q13 считают концерты по площадкам с HAVING. Значения подставляются "
    "только через плейсхолдеры. Представления concerts и venues читают данные через "
    "db/loaders.py из SQLite с откатом на JSON при отсутствии базы. README обновлён, "
    "исходники лежат в репозитории https://github.com/vladcheck/frameworks-python-system-project-5c."
)

r.h1("3 Результат работы")
r.numbered([
    "Создана схема из четырёх таблиц с первичными и внешними ключами.",
    "Данные перенесены из JSON в SQLite скриптом db/import_json.py.",
    "Написаны тринадцать запросов Q01 по Q13: списки, фильтры, JOIN, агрегаты и GROUP BY.",
    "Представления читают данные из SQLite с откатом на JSON, ORM не используется.",
])

r.h1("4 Проверка")
t2 = r.table(
    [
        ["Проверка", "Итог"],
        ["python manage.py check", "Ошибок нет"],
        ["pytest", "136 тестов проходят"],
        ["flake8", "Замечаний нет"],
        ["Страницы списков и деталей", "Код 200"],
        ["Чужой адрес или id", "Страница 404"],
    ],
    caption="Проверки проекта после ПР7",
)
r.text(
    f"Итоги проверок сведены {r.ref.in_table(t2)}. Изменения зафиксированы коммитом 5e928e7 "
    "с сообщением ПР7: sqlite хранилище и запросы. "
    "Репозиторий https://github.com/vladcheck/frameworks-python-system-project-5c."
)

r.h1("Заключение", center=True)
r.text(
    "Работа выполнена: спроектирована база SQLite, данные перенесены из JSON, написаны "
    "запросы всех видов, чтение из базы подключено к представлениям. Проект готов к "
    "переходу на Django ORM."
)

r.bib.add(
    "python-sqlite3",
    type="web",
    authors=["Python Software Foundation"],
    title="sqlite3, интерфейс DB-API 2.0 для баз данных SQLite",
    url="https://docs.python.org/3/library/sqlite3.html",
    accessed="16.10.2026",
)
r.bib.add(
    "sqlite-select",
    type="web",
    authors=["SQLite"],
    title="SELECT",
    url="https://sqlite.org/lang_select.html",
    accessed="16.10.2026",
)
r.bib.add(
    "sqlite-cli",
    type="web",
    authors=["SQLite"],
    title="Command Line Shell For SQLite",
    url="https://sqlite.org/cli.html",
    accessed="16.10.2026",
)
r.bib.add(
    "praktikum-backend",
    type="web",
    authors=["Яндекс Практикум"],
    title="Бэкенд-разработка",
    url="https://practicum.yandex.ru/backend-developer/",
    accessed="12.10.2026",
)
r.bib.add(
    "mozilla-sql",
    type="web",
    authors=["MDN Web Docs"],
    title="SQL",
    url="https://developer.mozilla.org/ru/docs/Glossary/SQL",
    accessed="12.10.2026",
)
r.text(
    "Работа с базой из Python по "
    + r.bib.cite("python-sqlite3")
    + ", синтаксис выборки по "
    + r.bib.cite("sqlite-select")
    + ", утилита командной строки по "
    + r.bib.cite("sqlite-cli")
    + ", курс Практикума "
    + r.bib.cite("praktikum-backend")
    + ", понятие SQL по "
    + r.bib.cite("mozilla-sql")
    + "."
)
r.bib.references()

out = r.save("ПР7_Отчет.docx")
print(f"Wrote {out}")
