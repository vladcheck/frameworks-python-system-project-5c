"""Модель исполнителя (ПР9: слой данных на Django ORM)."""

from django.db import models


class Performer(models.Model):
    """Исполнитель концертных выступлений."""

    name = models.CharField(
        max_length=200,
        verbose_name="Имя исполнителя",
    )
    genre = models.CharField(
        max_length=100,
        verbose_name="Жанр",
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        verbose_name="Рейтинг",
    )

    class Meta:
        # Сортировка по имени по умолчанию.
        ordering = ["name"]
        verbose_name = "Исполнитель"
        verbose_name_plural = "Исполнители"

    def __str__(self):
        """Вернуть строковое представление исполнителя."""
        return f"{self.name} ({self.genre})"
