"""Модель концертной площадки (ПР9: слой данных на Django ORM)."""

from django.db import models


class Venue(models.Model):
    """Концертная площадка."""

    name = models.CharField(
        max_length=200,
        verbose_name="Название площадки",
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Город",
    )
    capacity = models.PositiveIntegerField(
        verbose_name="Вместимость",
    )

    class Meta:
        # Сортировка по названию по умолчанию.
        ordering = ["name"]
        verbose_name = "Площадка"
        verbose_name_plural = "Площадки"

    def is_suitable_for(self, people_count: int) -> bool:
        """Проверить, вмещает ли площадка указанное число зрителей."""
        return self.capacity >= people_count

    def __str__(self):
        """Вернуть строковое представление площадки."""
        return f"{self.name}, {self.city} ({self.capacity} мест)"
