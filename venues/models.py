"""Модель концертной площадки (ПР9: слой данных на Django ORM)."""

from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.text import slugify


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
    slug = models.SlugField(
        "Слаг",
        max_length=200,
        unique=True,
        blank=True,
    )
    is_large = models.GeneratedField(
        expression=Q(capacity__gte=500),
        output_field=models.BooleanField(),
        db_persist=True,
        verbose_name="Большая площадка",
    )

    class Meta:
        # Сортировка по названию по умолчанию.
        ordering = ["name"]
        verbose_name = "Площадка"
        verbose_name_plural = "Площадки"

    def get_absolute_url(self):
        """Вернуть канонический адрес страницы площадки."""
        return reverse("venues:venue_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        """Сгенерировать уникальный слаг из названия при первом сохранении."""
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True) or "venue"
            slug = base_slug
            suffix = 2
            while (
                Venue.objects.filter(slug=slug)
                .exclude(pk=self.pk)
                .exists()
            ):
                slug = f"{base_slug}-{suffix}"
                suffix += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def is_suitable_for(self, people_count: int) -> bool:
        """Проверить, вмещает ли площадка указанное число зрителей."""
        return self.capacity >= people_count

    def __str__(self):
        """Вернуть строковое представление площадки."""
        return f"{self.name}, {self.city} ({self.capacity} мест)"
