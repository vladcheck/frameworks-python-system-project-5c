"""Модель концертной программы (ПР9: слой данных на Django ORM)."""

from django.db import models


class Program(models.Model):
    """Концертная программа."""

    name = models.CharField(
        max_length=200,
        verbose_name="Название программы",
    )
    duration = models.PositiveIntegerField(
        verbose_name="Продолжительность, мин",
    )
    age_limit = models.PositiveIntegerField(
        verbose_name="Возрастное ограничение",
    )

    class Meta:
        # Сортировка по названию по умолчанию.
        ordering = ["name"]
        verbose_name = "Программа"
        verbose_name_plural = "Программы"

    def is_allowed_for(self, guest_age: int) -> bool:
        """Проверить допуск зрителя по возрастному ограничению."""
        return guest_age >= self.age_limit

    def __str__(self):
        """Вернуть строковое представление программы."""
        return f"{self.name}, {self.duration} мин"
