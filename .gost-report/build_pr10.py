"""Отчёт ПР10: административная панель Django и работа с данными через ORM.

Структура по методичке, раздел 7.4: цель, материалы Практикума,
настройка админ-зоны, изменения моделей и миграций, работа с данными,
анализ SQL и Debug Toolbar, результат и проверка, вывод, источники.
"""
from gost_report import MIREA_PROFILE, Report, TitleConfig

r = Report(
    TitleConfig(
        work_type="Практическая работа",
        work_number="№10",
        topic="Административная панель Django и работа с данными через ORM",
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
    accessed="09.11.2026",
)
r.bib.add(
    "django-admin",
    type="web",
    authors=["Django Software Foundation"],
    title="The Django admin site",
    url="https://docs.djangoproject.com/en/5.2/ref/contrib/admin/",
    accessed="09.11.2026",
)
r.bib.add(
    "django-queries",
    type="web",
    authors=["Django Software Foundation"],
    title="Making queries",
    url="https://docs.djangoproject.com/en/5.2/topics/db/queries/",
    accessed="09.11.2026",
)
r.bib.add(
    "django-queryset",
    type="web",
    authors=["Django Software Foundation"],
    title="QuerySet API reference",
    url="https://docs.djangoproject.com/en/5.2/ref/models/querysets/",
    accessed="09.11.2026",
)
r.bib.add(
    "django-migrations",
    type="web",
    authors=["Django Software Foundation"],
    title="Migrations",
    url="https://docs.djangoproject.com/en/5.2/topics/migrations/",
    accessed="09.11.2026",
)
r.bib.add(
    "django-generated-field",
    type="web",
    authors=["Django Software Foundation"],
    title="GeneratedField",
    url="https://docs.djangoproject.com/en/5.2/ref/models/fields/#generatedfield",
    accessed="09.11.2026",
)
r.bib.add(
    "django-debug-toolbar",
    type="web",
    authors=["Jazzband"],
    title="django-debug-toolbar documentation",
    url="https://django-debug-toolbar.readthedocs.io/en/latest/",
    accessed="09.11.2026",
)

r.toc_static([
    (1, "Введение", 4),
    (1, "1 Материалы Яндекс Практикума", 5),
    (1, "2 Настройка административной панели", 6),
    (1, "3 Изменения моделей и миграций", 8),
    (1, "4 Работа с данными через ORM", 10),
    (1, "5 Анализ SQL и Django Debug Toolbar", 12),
    (1, "6 Результат и проверка", 14),
    (1, "Вывод", 16),
    (1, "Список использованных источников", 17),
])

r.h1("Введение", center=True)
r.text(
    "Цель работы по методичке: освоить административную панель Django и углубить "
    "навыки работы с данными через ORM. В проекте Concerty это означает: "
    "зарегистрировать все модели в админ-зоне и настроить её под задачи "
    "контент-менеджера, заменить булево поле is_cancelled концертов на полноценный "
    "статус жизненного цикла, добавить площадкам слаг и вычисляемое поле "
    "is_large, подключить django-debug-toolbar и анализировать реальные "
    "SQL-запросы страниц. Материалы курса «Бэкенд-разработка» дают приёмы "
    "тонкой настройки админ-зоны и построения запросов "
    + r.bib.cite("praktikum-backend")
    + "."
)

r.h1("1 Материалы Яндекс Практикума")
r.text(
    "Выполнены материалы разделов «Административная панель Django» и «Работа с "
    "данными через ORM» курса «Бэкенд-разработка». Перечень тем и отметки о "
    "выполнении приведены ниже."
)
t1 = r.table(
    [
        ["Тема", "Отметка о выполнении"],
        ["Админ-зона Django: суперпользователь и регистрация моделей", "Выполнено"],
        ["Локализация и перевод", "Выполнено"],
        ["Тонкая настройка админ-зоны", "Выполнено"],
        ["Django ORM, получение информации из БД: Debug Toolbar", "Выполнено"],
        ["SELECT и FROM через ORM", "Выполнено"],
        ["filter() и exclude()", "Выполнено"],
        ["Q-объекты", "Выполнено"],
        ["order_by(), limit и offset", "Выполнено"],
        ["Получение отдельных объектов", "Выполнено"],
        ["Запросы к связанным моделям", "Выполнено"],
        ["Доработка проекта", "Выполнено"],
        ["Финальный проект спринта: публикации для Блогикум", "Выполнено"],
    ],
    caption="Материалы курса «Бэкенд-разработка» по теме работы",
)
r.text(
    "Все двенадцать тем "
    + r.ref.in_table(t1)
    + " отмечены как выполненные, приёмы повторены на данных проекта Concerty."
)

r.h1("2 Настройка административной панели")
r.text(
    "В административной панели зарегистрированы все четыре модели: Performer, "
    "Venue, Program и Concert. Для каждой модели написан класс ModelAdmin "
    "с параметрами списка записей. Основной приём настройки: вывести в список "
    "только нужные поля, дать ссылки на ключевые колонки, добавить фильтры и "
    "поиск, включить постраничный вывод по 20 записей "
    + r.bib.cite("django-admin")
    + "."
)
t2 = r.table(
    [
        ["Модель", "List display", "List display links", "List filter", "Search fields"],
        [
            "Concert",
            "id, title, date, performer, venue, status",
            "title",
            "status, date, venue",
            "title, performer__name, venue__name",
        ],
        [
            "Venue",
            "id, name, city, capacity, slug, is_large",
            "name",
            "city, is_large",
            "name, city",
        ],
        ["Performer", "id, name, genre, rating", "name", "genre", "name, genre"],
        ["Program", "id, name, duration, age_limit", "name", "age_limit", "name"],
    ],
    caption="Параметры ModelAdmin по моделям проекта",
)
r.text(
    "Параметры списков приведены "
    + r.ref.in_table(t2)
    + ". У ConcertAdmin дополнительно заданы date_hierarchy по полю date "
    "(навигация по датам справа от списка), ordering по дате и идентификатору "
    "и list_select_related для связанных объектов. Код настройки показан "
    "в листинге ниже."
)
lst_admin = r.listing(
    """@admin.register(Concert)
class ConcertAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "date", "performer", "venue", "status")
    list_display_links = ("title",)
    list_filter = ("status", "date", "venue")
    search_fields = ("title", "performer__name", "venue__name")
    # Связанные объекты загружаются одним запросом.
    list_select_related = ("performer", "venue", "program")
    date_hierarchy = "date"
    ordering = ("date", "pk")
    list_per_page = 20""",
    "Настройка ConcertAdmin в concerts/admin.py",
)
r.text(
    "Фрагмент настройки списка концертов приведён "
    + r.ref.on_listing(lst_admin)
    + ". Поиск по связанным моделям работает через обращение через внешний "
    "ключ performer__name."
)
lst_inline = r.listing(
    """class ConcertInline(admin.TabularInline):
    model = Concert
    fields = ("title", "performer", "program", "date", "status")
    readonly_fields = fields
    extra = 0
    can_delete = False

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    ...
    inlines = (ConcertInline,)""",
    "Инлайн концертов в карточке площадки в venues/admin.py",
)
r.text(
    "В карточки площадки, исполнителя и программы добавлен инлайн-просмотр "
    "связанных концертов "
    + r.ref.on_listing(lst_inline)
    + ". Поля инлайна только для чтения, удаление отключено: внешние ключи "
    "Concert защищены PROTECT, поэтому менять список концертов из чужой "
    "карточки нельзя, а удалить их и вовсе не выйдет."
)
r.text(
    "Локализация: в пяти приложениях заданы AppConfig с русскими verbose_name, "
    "у моделей переведены названия и множественные формы, в settings.py "
    "установлен LANGUAGE_CODE ru-RU. На странице редактирования площадки "
    "появилась ссылка «Смотреть на сайте», она строится методом "
    "get_absolute_url модели Venue."
)

r.h1("3 Изменения моделей и миграций")
r.text(
    "Булево поле is_cancelled заменено на поле status с вариантами выбора "
    "Concert.Status (TextChoices): SCHEDULED, CANCELLED, COMPLETED. Поверх "
    "поля построены менеджер ConcertManager и класс запросов ConcertQuerySet "
    "с методами scheduled, cancelled, completed и for_date. Код приведён "
    "ниже."
)
lst_model = r.listing(
    """class ConcertQuerySet(models.QuerySet):
    def scheduled(self):
        return self.filter(status=Concert.Status.SCHEDULED)

    def cancelled(self):
        return self.filter(status=Concert.Status.CANCELLED)

    def completed(self):
        return self.filter(status=Concert.Status.COMPLETED)

    def for_date(self, concert_date):
        return self.filter(date=concert_date)

class Concert(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Запланирован"
        CANCELLED = "CANCELLED", "Отменён"
        COMPLETED = "COMPLETED", "Завершён"
    ...
    status = models.CharField(max_length=20, choices=Status.choices, ...)
    objects = ConcertManager()""",
    "Статусы и менеджер концертов в concerts/models.py",
)
r.text(
    "Менеджер и статусы "
    + r.ref.on_listing(lst_model)
    + " дают читаемые вызовы Concert.objects.scheduled() вместо повторяющихся "
    "filter(status=...). Порядок миграций описан в документации Django "
    + r.bib.cite("django-migrations")
    + "."
)
r.text(
    "Переход выполнен тремя миграциями: 0002_concert_status добавляет поле "
    "status, 0003_migrate_concert_status переносит данные (истина в "
    "is_cancelled стала CANCELLED, прошедшие даты стали COMPLETED, остальное "
    "SCHEDULED), 0004_remove_concert_is_cancelled удаляет старое поле. "
    "У площадок миграции: 0002_venue_is_large_venue_slug добавляет слаг и "
    "GeneratedField is_large, 0003_fill_venue_slugs заполняет слаги у "
    "существующих записей, 0004_alter_venue_slug делает слаг уникальным."
)
r.text(
    "Поле Venue.slug заполняется автоматически из названия при первом "
    "сохранении, кириллица сохраняется. Для маршрута площадки зарегистрирован "
    "конвертер uslug на основе UnicodeSlugConverter, потому что стандартный "
    "конвертер slug кириллицу не пропускает. Вместимость площадки не меньше "
    "500 мест отражает вычисляемое поле is_large: GeneratedField "
    "с выражением Q по полю capacity__gte (вместимость не меньше 500) "
    "и параметром db_persist равным True, значение "
    "хранится в базе и обновляется самой СУБД "
    + r.bib.cite("django-generated-field")
    + "."
)

r.h1("4 Работа с данными через ORM")
r.text(
    "Представления построены на запросах ORM и описаны в документации Django "
    + r.bib.cite("django-queries", "django-queryset")
    + ". Список концертов фильтруется по статусу, дате, площадке и "
    "исполнителю через filter, поиск собирается Q-объектами с icontains по "
    "названию и имени исполнителя. Сортировка идёт только по белому списку "
    "SORT_FIELDS, параметр из адресной строки подставляется в order_by без "
    "возможности SQL-инъекции. Пагинация Paginator выводит по шесть записей "
    "на страницу, параметры фильтров сохраняются при переходе по страницам "
    "шаблонным тегом querystring. Детальная страница концерта и карточка "
    "площадки берут объекты через get_object_or_404 с select_related. "
    "Страница статистики использует values, annotate и aggregate: счётчики, "
    "суммы и средние по трём статусам концертов."
)
r.text(
    "Подбор свободных площадок на дату строится на exclude: идентификаторы "
    "площадок с запланированными концертами на выбранную дату убираются из "
    "общего списка. Отменённые и завершённые концерты площадку не блокируют. "
    "Проверка логики в Django shell приведена ниже."
)
lst_shell = r.listing(
    """(a) scheduled: 4
(a) cancelled: 0
(a) completed: 11
(b) for_date 2026-11-14 -> 1
(c) venue 11 absent from free list on 2026-11-14 : True
(c) completed concert 5 venue 4 present in free list: True
(c2) cancelled concert 160 venue 9 present in free list: True
(c2) temp cancelled concert deleted
(d) slug: adrenaline-stadium
(d) url: /venues/adrenaline-stadium/
(e) capacity=499 is_large: False
(e) capacity=500 is_large: True
(e) temp venue deleted""",
    "Транскрипт проверки ORM в Django shell",
)
r.text(
    "Транскрипт "
    + r.ref.on_listing(lst_shell)
    + " подтверждает: менеджер считает концерты по статусам, for_date "
    "выбирает концерты даты, площадка с запланированным концертом исключена "
    "из списка свободных, площадки с завершённым и отменённым концертами в "
    "списке присутствуют. Слаг и адрес первой площадки отвечают "
    "get_absolute_url, а GeneratedField меняет is_large на границе "
    "вместимости 500 мест."
)

r.h1("5 Анализ SQL и Django Debug Toolbar")
r.text(
    "django-debug-toolbar 8.0 подключён четырьмя правками: приложение "
    "debug_toolbar добавлено в INSTALLED_APPS, DebugToolbarMiddleware "
    "вставлен в MIDDLEWARE, INTERNAL_IPS ограничен адресами localhost и "
    "127.0.0.1, маршрут __debug__/ подключается в urls.py только при DEBUG "
    "равном истине. Зависимости зафиксированы в pyproject.toml, uv.lock и "
    "requirements.txt. Панель показывает SQL-запросы страницы, их время и "
    "план выполнения "
    + r.bib.cite("django-debug-toolbar")
    + "."
)
r.text(
    "Число запросов страниц измерено через django.test.utils."
    "CaptureQueriesContext, итоги приведены ниже."
)
t3 = r.table(
    [
        ["Страница", "Код ответа", "Число запросов"],
        ["/concerts/", "200", "5"],
        ["/concerts/8/", "200", "2"],
        ["/venues/", "200", "3"],
        ["/venues/available/?date=2026-11-14", "200", "2"],
    ],
    caption="Число SQL-запросов на страницу в тестовом клиенте",
)
r.text(
    "Числа "
    + r.ref.in_table(t3)
    + " сняты без панели инструментов, лишние запросы шаблонов отсутствуют. "
    "Главный SELECT детальной страницы концерта показан ниже."
)
lst_sql = r.listing(
    """SELECT "concerts_concert"."id", "concerts_concert"."title",
 "concerts_concert"."performer_id", "concerts_concert"."venue_id",
 "concerts_concert"."program_id", "concerts_concert"."date",
 "concerts_concert"."expected_guests", "concerts_concert"."base_ticket_price",
 "concerts_concert"."status", "performers_performer"."id",
 "performers_performer"."name", "performers_performer"."genre",
 "performers_performer"."rating", "venues_venue"."id", "venues_venue"."name",
 "venues_venue"."city", "venues_venue"."capacity", "venues_venue"."slug",
 "venues_venue"."is_large", "programs_program"."id", "programs_program"."name",
 "programs_program"."duration", "programs_program"."age_limit"
FROM "concerts_concert"
INNER JOIN "performers_performer"
 ON ("concerts_concert"."performer_id" = "performers_performer"."id")
INNER JOIN "venues_venue"
 ON ("concerts_concert"."venue_id" = "venues_venue"."id")
INNER JOIN "programs_program"
 ON ("concerts_concert"."program_id" = "programs_program"."id")
WHERE "concerts_concert"."id" = 8 LIMIT 21""",
    "SQL детальной страницы концерта с JOIN от select_related",
)
r.text(
    "Запрос "
    + r.ref.on_listing(lst_sql)
    + " выполняется один раз: select_related собирает исполнителя, площадку "
    "и программу тремя JOIN в том же SELECT. Без select_related каждая связь "
    "дала бы отдельный запрос, и страница выборки из N концертов породила бы "
    "один основной и по три дополнительных запроса на каждый концерт, "
    "то есть рост числа запросов линейный по N, это известная проблема "
    "N плюс один запрос. "
    "План запроса менеджера "
    "Concert.objects.scheduled() подтверждает простой обход таблицы "
    "concerts_concert и сортировку через временное B-дерево по полю ordering "
    "модели."
)
lst_explain = r.listing(
    """3 0 216 SCAN concerts_concert
19 0 0 USE TEMP B-TREE FOR ORDER BY""",
    "План запроса Concert.objects.scheduled() по .explain()",
)
r.text(
    "План запроса приведён "
    + r.ref.on_listing(lst_explain)
    + ": SQLite читает таблицу целиком, индексов на фильтруемые поля в учебной "
    "базе не создано, для объёма данных проекта этого достаточно."
)

r.h1("6 Результат и проверка")
r.numbered([
    "Зарегистрированы четыре модели в админ-зоне с фильтрами, поиском, "
    "иерархией по дате и постраничным выводом по 20 записей.",
    "Добавлены инлайн-формы концертов в карточки площадки, исполнителя и "
    "программы, удаление в инлайнах отключено из-за PROTECT.",
    "Поле is_cancelled заменено статусами TextChoices с менеджером "
    "ConcertQuerySet, данные перенесены миграцией.",
    "Площадки получили автоматические слаги с поддержкой кириллицы и "
    "GeneratedField is_large на границе 500 мест.",
    "Контекстный процессор concert_context передаёт site_name и число "
    "концертов в base.html и навигацию, интерфейс полностью локализован.",
    "Подключён django-debug-toolbar, SQL-запросы страниц проанализированы, "
    "проблема N плюс 1 не выявлена.",
])

r.h2("6.1 Проверка команд")
r.text("Команды проверки запущены из корня проекта, их результаты приведены ниже.")
t4 = r.table(
    [
        ["Команда", "Результат"],
        ["python manage.py check", "System check identified no issues (0 silenced)"],
        ["python manage.py makemigrations --check", "No changes detected"],
        [
            "python manage.py showmigrations",
            "Отметка [X] у миграций 0002-0004 приложений concerts и venues",
        ],
        ["pytest -q", "246 passed in 8.16s"],
        ["flake8 . --extend-exclude=venv", "Замечаний нет, код выхода 0"],
    ],
    caption="Результаты проверок проекта",
)
r.text(
    "Все проверки "
    + r.ref.in_table(t4)
    + " проходят без ошибок, миграции применены к базе."
)

r.h2("6.2 Пользовательские сценарии")
t5 = r.table(
    [
        ["Сценарий", "Результат"],
        ["Главная, списки концертов и площадок", "Открываются, данные из ORM"],
        ["Фильтры и поиск списка концертов", "Работают, параметры сохраняются"],
        ["Пагинация по шесть записей", "Переключение страниц сохраняет фильтры"],
        ["Несуществующий слаг площадки", "Страница 404"],
        ["Страница статистики", "Агрегаты по трём статусам концертов"],
        ["Подбор площадок на дату", "Список свободных площадок корректен"],
    ],
    caption="Проверенные пользовательские сценарии",
)
r.text(
    "Сценарии "
    + r.ref.in_table(t5)
    + " покрыты автотестами tests/test_pr10.py и ручной проверкой."
)

r.h2("6.3 Git")
r.text(
    "Работа выполнена в ветке main. Изменения ПР10 зафиксированы тремя "
    "коммитами."
)
t6 = r.table(
    [
        ["Коммит", "Сообщение"],
        ["a4afe54", "статусы концертов, слаги площадок, GeneratedField is_large, миграции данных"],
        ["295107f", "админ-зона с инлайнами, контекстный процессор, локализация, Debug Toolbar"],
        ["54da89d", "тесты, README и зависимости (debug-toolbar, pypdf)"],
    ],
    caption="Коммиты ПР10 в ветке main",
)
r.text(
    "Список коммитов приведён "
    + r.ref.in_table(t6)
    + ". Файлы отчёта добавляются отдельным коммитом после сборки."
)

r.h1("Вывод", center=True)
r.text(
    "Административная панель проекта настроена для контент-менеджера: модели "
    "зарегистрированы, списки отфильтрованы и переведены, концерты видны "
    "внутри карточек связанных сущностей. Модельный слой усилен статусами "
    "жизненного цикла, менеджером запросов, слагами и вычисляемым полем "
    "GeneratedField, переход данных выполнен миграциями без потерь. ORM "
    "даёт фильтрацию, поиск, сортировку и пагинацию, а Debug Toolbar и "
    "замер запросов подтвердили отсутствие лишних обращений к базе."
)

r.bib.references()

out = r.save("ПР10_Отчет.docx")
print(f"Wrote {out}")
