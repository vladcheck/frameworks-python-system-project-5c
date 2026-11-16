"""Формы приложения venues: редактирование площадки с загрузкой изображения."""

from django import forms

from .models import Venue


class VenueForm(forms.ModelForm):
    """Форма создания и редактирования концертной площадки."""

    class Meta:
        """Привязка к модели Venue и русские подписи полей."""

        model = Venue
        fields = ["name", "city", "capacity", "image"]
        labels = {
            "name": "Название площадки",
            "city": "Город",
            "capacity": "Вместимость",
            "image": "Изображение",
        }
        help_texts = {
            "image": "Необязательно. Файл будет загружен в каталог медиафайлов.",
        }
