"""Формы приложения concerts: фильтры списка и редактирование концерта."""

from django import forms
from django.utils import timezone

from performers.models import Performer
from venues.models import Venue

from .models import Concert


class ConcertFilterForm(forms.Form):
    """Форма фильтрации списка концертов (GET-параметры запроса)."""

    q = forms.CharField(required=False, label="Поиск")
    venue = forms.ModelChoiceField(
        queryset=Venue.objects.order_by("name"),
        required=False,
        label="Площадка",
        empty_label="Все площадки",
    )
    performer = forms.ModelChoiceField(
        queryset=Performer.objects.order_by("name"),
        required=False,
        label="Исполнитель",
        empty_label="Все исполнители",
    )
    status = forms.ChoiceField(
        required=False,
        label="Статус",
        choices=[
            ("", "Все концерты"),
            ("active", "Активные"),
            ("cancelled", "Отменённые"),
        ],
    )
    date_from = forms.DateField(
        required=False,
        label="Дата с",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    sort = forms.ChoiceField(
        required=False,
        label="Сортировать по",
        choices=[
            ("", "По умолчанию (дате)"),
            ("date", "Дате"),
            ("title", "Названию"),
            ("venue", "Площадке"),
            ("performer", "Исполнителю"),
        ],
    )


class ConcertForm(forms.ModelForm):
    """Форма создания и редактирования концерта."""

    class Meta:
        """Привязка к модели Concert и настройки виджетов Bootstrap."""

        model = Concert
        fields = [
            "title",
            "performer",
            "venue",
            "program",
            "date",
            "expected_guests",
            "base_ticket_price",
        ]
        labels = {
            "title": "Название",
            "performer": "Исполнитель",
            "venue": "Площадка",
            "program": "Программа",
            "date": "Дата концерта",
            "expected_guests": "Ожидается зрителей",
            "base_ticket_price": "Базовая цена билета",
        }
        help_texts = {
            "venue": "Площадка должна вместить ожидаемое число зрителей.",
            "date": "Нельзя планировать концерт на прошедшую дату.",
        }
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "performer": forms.Select(attrs={"class": "form-select"}),
            "venue": forms.Select(attrs={"class": "form-select"}),
            "program": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date", "class": "form-control"},
            ),
            "expected_guests": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "base_ticket_price": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
        }

    def clean_date(self):
        """Запретить планирование концерта на прошедшую дату."""
        concert_date = self.cleaned_data["date"]
        if concert_date < timezone.localdate():
            raise forms.ValidationError(
                "Нельзя планировать концерт на прошедшую дату."
            )
        return concert_date

    def clean(self):
        """Проверить правило предметной области: площадка вмещает зрителей."""
        cleaned_data = super().clean()
        venue = cleaned_data.get("venue")
        expected_guests = cleaned_data.get("expected_guests")
        if (
            venue is not None
            and expected_guests is not None
            and not venue.is_suitable_for(expected_guests)
        ):
            self.add_error(
                "expected_guests",
                "Площадка не вмещает всех зрителей.",
            )
        return cleaned_data
