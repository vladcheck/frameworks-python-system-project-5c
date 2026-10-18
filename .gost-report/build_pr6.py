"""Отчёт ПР6: Шаблоны Django и проектная разработка.

Структура по методичке, раздел 7.5: общие сведения, цель, материалы Практикума,
доработка проекта, результат, проверка, Git, вывод. Объём 1-2 страницы без титула.
"""
from gost_report import MIREA_PROFILE, Report, TitleConfig

r = Report(
    TitleConfig(
        work_type="Практическая работа",
        work_number="№6",
        topic="Шаблоны Django и проектная разработка",
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
    "Цель работы освоить шаблоны Django и перевести на них веб-интерфейс Concerty из ПР5: "
    "уйти от сборки HTML в Python функциях к схеме View, Context, Template, HTML, сохранив "
    "предметную область, JSON хранилище и работоспособность кода."
)

r.h1("1 Материалы Яндекс Практикума")
r.text(
    "Выполнены материалы раздела 04: тема «HTML и шаблоны Django» (шаблоны страниц, теги "
    "include, extends и block, контекст, ветвление и циклы, именованные URL, фильтры, статика) "
    "и финальный проект спринта Блогикум."
)

r.h1("2 Доработка проекта")
r.text(
    "Создана структура шаблонов: каталог templates с base.html и includes/navigation.html, "
    "в каждом приложении свои списки, детали и карточки. Каталог проекта добавлен в DIRS, "
    "поиск в приложениях оставлен через APP_DIRS. Base содержит структуру документа, Bootstrap, "
    "свой CSS, логотип, навигацию, блоки title и content, подвал и скрипт. Повторы вынесены "
    "в include: карточки сущностей и статус концерта."
)
lst = r.listing(
    "return render(request, 'concerts/concert_list.html', {'concerts': cs})",
    "View-функция передаёт контекст в шаблон через render",
)
r.text(
    f"Представления переведены с HttpResponse на render, функция page из ПР5 удалена "
    f"{r.ref.on_listing(lst)}. В шаблонах работают for с empty, if и else, фильтры length, "
    "default и date. Ссылки идут только через url с пространствами homepage, concerts, venues, "
    "performers и programs. Статика homepage/static/homepage: style.css, main.js и logo.png."
)

r.h1("3 Результат работы")
r.numbered([
    "Десять страниц на шаблонах: главная, списки и детали концертов, площадок, исполнителей и программ.",
    "Наследование через extends, повторы через include, данные через контекст.",
    "Именованные URL, фильтры length, default и date, собственная статика.",
    "Модель ПР3 и JSON хранилище сохранены, ORM на этом этапе не используется.",
])

r.h1("4 Проверка")
t2 = r.table(
    [
        ["Проверка", "Итог"],
        ["python manage.py check", "Ошибок нет"],
        ["pytest", "Тесты проходят"],
        ["flake8", "Замечаний нет"],
        ["Десять страниц", "Код 200"],
        ["Чужой адрес или id", "Страница 404"],
    ],
    caption="Проверки проекта после ПР6",
)
r.text(
    f"Итоги проверок сведены {r.ref.in_table(t2)}. Изменения зафиксированы коммитами с меткой "
    "PR6: базовый шаблон, перевод страниц на шаблоны, статика и README. "
    "Репозиторий https://github.com/vladcheck/frameworks-python-system-project-5c."
)

r.h1("Заключение", center=True)
r.text(
    "Работа выполнена: веб-часть переведена на шаблоны Django, генерация HTML в Python "
    "убрана. Проект готов к переходу на базу данных и Django ORM."
)

r.bib.add(
    "django-templates",
    type="web",
    authors=["Django Software Foundation"],
    title="Django template language",
    url="https://docs.djangoproject.com/en/5.2/ref/templates/language/",
    accessed="10.10.2026",
)
r.bib.add(
    "django-static",
    type="web",
    authors=["Django Software Foundation"],
    title="Managing static files",
    url="https://docs.djangoproject.com/en/5.2/howto/static-files/",
    accessed="08.10.2026",
)
r.bib.add(
    "praktikum-backend",
    type="web",
    authors=["Яндекс Практикум"],
    title="Бэкенд-разработка",
    url="https://practicum.yandex.ru/backend-developer/",
    accessed="06.10.2026",
)
r.bib.add(
    "bootstrap-docs",
    type="web",
    authors=["Bootstrap"],
    title="Bootstrap documentation",
    url="https://getbootstrap.com/docs/5.3/",
    accessed="06.10.2026",
)
r.bib.add(
    "mozilla-css",
    type="web",
    authors=["MDN Web Docs"],
    title="Руководство по CSS",
    url="https://developer.mozilla.org/ru/docs/Web/CSS",
    accessed="06.10.2026",
)
r.text(
    "Язык шаблонов "
    + r.bib.cite("django-templates")
    + ", статика по "
    + r.bib.cite("django-static")
    + ", курс Практикума "
    + r.bib.cite("praktikum-backend")
    + ", оформление по "
    + r.bib.cite("bootstrap-docs")
    + " и "
    + r.bib.cite("mozilla-css")
    + "."
)
r.bib.references()

out = r.save("ПР6_Отчет.docx")
print(f"Wrote {out}")
