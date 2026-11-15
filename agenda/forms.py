from django import forms
from django.utils.timezone import localdate

from .models import Event, Interest, Visitor

DATE_WIDGET = forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})
EVENT_ORDER = (("date", "По дате"), ("price", "По цене"), ("name", "По названию"))
RECOMMENDATION_ORDER = (("score", "По совпадению"), *EVENT_ORDER)


class EventFilterForm(forms.Form):
    q = forms.CharField(
        label="Поиск", required=False, max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Название или место"}),
    )
    interest = forms.ModelChoiceField(
        label="Интерес", required=False, queryset=Interest.objects.all(),
        empty_label="Все интересы",
    )
    start = forms.DateField(
        label="Начиная с даты", required=False,
        input_formats=["%Y-%m-%d"], widget=DATE_WIDGET,
    )
    price = forms.DecimalField(
        label="До, ₽", min_value=0, max_digits=9, decimal_places=2, required=False,
    )
    sort = forms.ChoiceField(label="Сортировка", choices=EVENT_ORDER, required=False)


class RecommendationFilterForm(EventFilterForm):
    sort = forms.ChoiceField(
        label="Сортировка", choices=RECOMMENDATION_ORDER, required=False,
    )
    status = forms.ChoiceField(
        label="Статус",
        choices=(("current", "Подходящие"), ("saved", "Сохранённые"),
                 ("dismissed", "Отклонённые")),
        required=False,
    )


class VisitorForm(forms.ModelForm):
    budget = forms.DecimalField(
        label="Бюджет на событие, ₽", min_value=0, max_digits=9, decimal_places=2,
    )

    class Meta:
        model = Visitor
        fields = ("name", "age", "budget", "interests")
        widgets = {"interests": forms.CheckboxSelectMultiple}
        help_texts = {"interests": "Выберите темы для персональной подборки."}


class EventForm(forms.ModelForm):
    price = forms.DecimalField(
        label="Цена, ₽", min_value=0, max_digits=9, decimal_places=2,
    )

    class Meta:
        model = Event
        fields = (
            "name", "date", "venue", "description", "price", "min_age",
            "interests", "poster", "active",
        )
        widgets = {"date": DATE_WIDGET, "interests": forms.CheckboxSelectMultiple,
                   "description": forms.Textarea(attrs={"rows": 5})}
        help_texts = {"poster": "JPG, PNG или WebP, до 5 МБ."}

    def clean(self):
        data = super().clean()
        event_date = data.get("date")
        if (data.get("active") and event_date and event_date < localdate()
                and (not self.instance.pk or self.instance.date != event_date
                     or not self.instance.active)):
            self.add_error("date", "Выберите сегодняшнюю или будущую дату.")
        return data

    def clean_poster(self):
        image = self.cleaned_data["poster"]
        if hasattr(image, "image") and image.image.format not in {"JPEG", "PNG", "WEBP"}:
            raise forms.ValidationError("Загрузите изображение в JPG, PNG или WebP.")
        return image
