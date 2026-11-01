"""Модель концерта и связи с исполнителем, площадкой и программой."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import models

from performers.models import Performer
from programs.models import Program
from venues.models import Venue


class Concert(models.Model):
    """Концертное выступление.

    Связывает исполнителя, площадку и программу внешними ключами:
    у одного исполнителя, площадки или программы может быть много
    концертов, а каждый концерт ссылается на одну запись каждого вида.
    """

    title = models.CharField(
        max_length=200,
        verbose_name="Название концерта",
    )
    performer = models.ForeignKey(
        Performer,
        on_delete=models.PROTECT,
        related_name="concerts",
        verbose_name="Исполнитель",
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        related_name="concerts",
        verbose_name="Площадка",
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.PROTECT,
        related_name="concerts",
        verbose_name="Программа",
    )
    date = models.DateField(
        verbose_name="Дата концерта",
    )
    expected_guests = models.PositiveIntegerField(
        verbose_name="Ожидается зрителей",
    )
    base_ticket_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Базовая цена билета, руб.",
    )
    is_cancelled = models.BooleanField(
        default=False,
        verbose_name="Концерт отменён",
    )

    class Meta:
        # Сначала по дате, затем по идентификатору.
        ordering = ["date", "pk"]
        verbose_name = "Концерт"
        verbose_name_plural = "Концерты"

    def get_status(self, today: date | None = None) -> str:
        """Определить статус концерта относительно даты."""
        today = today or date.today()
        if self.is_cancelled:
            return "Отменён"
        if self.date > today:
            return "Запланирован"
        if self.date == today:
            return "Идёт сегодня"
        return "Завершён"

    def calculate_ticket_price(self) -> Decimal:
        """Рассчитать цену билета с учётом рейтинга исполнителя."""
        if self.performer.rating >= Decimal("9.0"):
            multiplier = Decimal("1.5")
        elif self.performer.rating >= Decimal("7.0"):
            multiplier = Decimal("1.2")
        else:
            multiplier = Decimal("1.0")
        price = self.base_ticket_price * multiplier
        return price.quantize(Decimal("0.01"))

    def check_venue_fit(self) -> str:
        """Проверить, вмещает ли площадка ожидаемое число зрителей."""
        if self.venue.is_suitable_for(self.expected_guests):
            free_seats = self.venue.capacity - self.expected_guests
            return f"Площадка подходит, свободных мест: {free_seats}"
        return "Площадка не вмещает всех зрителей"

    def calculate_revenue(self) -> Decimal:
        """Рассчитать ожидаемую выручку концерта."""
        return self.calculate_ticket_price() * self.expected_guests

    def cancel(self) -> None:
        """Отменить концерт и сохранить только изменённое поле."""
        self.is_cancelled = True
        self.save(update_fields=["is_cancelled"])

    def __str__(self):
        """Вернуть строковое представление концерта."""
        return f"{self.title} ({self.date:%d.%m.%Y})"
