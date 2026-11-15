from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MaxValueValidator
from django.db import models
from django.db.models import Q
from django.urls import reverse

AGE_LIMIT = 120


def validate_poster_size(image):
    if image.size > 5 * 1024 * 1024:
        raise ValidationError("Изображение должно занимать не более 5 МБ.")


class Interest(models.Model):
    name = models.CharField("название", max_length=80, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "интерес"
        verbose_name_plural = "интересы"

    def __str__(self):
        return self.name


class Visitor(models.Model):
    account = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="visitor",
        blank=True, null=True, verbose_name="учётная запись",
    )
    name = models.CharField("имя", max_length=100)
    age = models.PositiveSmallIntegerField("возраст", validators=[MaxValueValidator(AGE_LIMIT)])
    budget = models.DecimalField("бюджет, ₽", max_digits=9, decimal_places=2)
    interests = models.ManyToManyField(
        Interest, related_name="visitors", blank=True, verbose_name="интересы",
    )

    class Meta:
        ordering = ("name", "pk")
        verbose_name = "профиль пользователя"
        verbose_name_plural = "профили пользователей"
        constraints = [
            models.CheckConstraint(
                condition=Q(age__range=(0, AGE_LIMIT)), name="visitor_age_in_range",
            ),
            models.CheckConstraint(condition=Q(budget__gte=0), name="visitor_budget_positive"),
        ]

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField("название", max_length=150)
    date = models.DateField("дата")
    price = models.DecimalField("цена, ₽", max_digits=9, decimal_places=2)
    min_age = models.PositiveSmallIntegerField(
        "возрастное ограничение", default=0, validators=[MaxValueValidator(AGE_LIMIT)],
    )
    active = models.BooleanField("в афише", default=True)
    venue = models.CharField("место проведения", max_length=150, blank=True)
    description = models.TextField("описание", blank=True)
    poster = models.ImageField(
        "афиша", upload_to="posters/%Y/%m/", blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=("jpg", "jpeg", "png", "webp")),
            validate_poster_size,
        ],
    )
    interests = models.ManyToManyField(Interest, related_name="events", verbose_name="интересы")

    class Meta:
        ordering = ("date", "id")
        verbose_name = "мероприятие"
        verbose_name_plural = "мероприятия"
        indexes = [models.Index(fields=("active", "date"), name="agenda_active_date")]
        constraints = [
            models.CheckConstraint(
                condition=Q(min_age__range=(0, AGE_LIMIT)), name="event_age_in_range",
            ),
            models.CheckConstraint(condition=Q(price__gte=0), name="event_price_positive"),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("agenda:event", args=[self.pk])


class Recommendation(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        SAVED = "saved", "Сохранена"
        DISMISSED = "dismissed", "Отклонена"

    visitor = models.ForeignKey(
        Visitor, on_delete=models.CASCADE, related_name="recommendations",
        verbose_name="пользователь",
    )
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="recommendations",
        verbose_name="мероприятие",
    )
    score = models.PositiveSmallIntegerField("общих интересов")
    status = models.CharField("статус", max_length=10, choices=Status, default=Status.NEW)

    class Meta:
        ordering = ("-score", "event__date", "event_id")
        verbose_name = "рекомендация"
        verbose_name_plural = "рекомендации"
        constraints = [
            models.UniqueConstraint(fields=("visitor", "event"), name="unique_recommendation"),
            models.CheckConstraint(condition=Q(score__gt=0), name="recommendation_positive_score"),
            models.CheckConstraint(
                condition=Q(status__in=("new", "saved", "dismissed")),
                name="recommendation_known_status",
            ),
        ]

    def __str__(self):
        return f"{self.visitor} · {self.event}"
