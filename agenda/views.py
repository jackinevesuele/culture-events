from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Count, F, OuterRef, Q, Subquery, Value
from django.db.models.functions import Coalesce
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import localdate
from django.views.decorators.http import require_POST

from .forms import EventFilterForm, EventForm, RecommendationFilterForm, VisitorForm
from .models import Event, Interest, Recommendation, Visitor
from .selectors import (
    EVENT_SORT, MATCH_SORT, matching_events, search_events, statistics,
    upcoming_events, with_tags,
)


def home(request):
    events = with_tags(upcoming_events())[:3]
    return render(request, "agenda/home.html", {"events": events})


def apply_filters(events, form, orders, default):
    if not form.is_valid():
        return events.none()
    options = form.cleaned_data
    return search_events(
        events, options["q"], options["interest"], options["start"], options["price"],
    ).order_by(*orders[options["sort"] or default])


def event_list(request):
    form = EventFilterForm(request.GET)
    events = apply_filters(upcoming_events(), form, EVENT_SORT, "date")
    page = Paginator(with_tags(events), 6).get_page(request.GET.get("page"))
    return render(request, "agenda/events.html", {"page": page, "form": form})


def event_detail(request, pk):
    events = Event.objects.all() if request.user.has_perm("agenda.change_event") \
        else Event.objects.filter(active=True)
    event = get_object_or_404(with_tags(events), pk=pk)
    return render(request, "agenda/event.html", {"event": event})


def interest_list(request):
    interests = Interest.objects.annotate(total=Count(
        "events", filter=Q(events__active=True, events__date__gte=localdate()),
    ))
    return render(request, "agenda/interests.html", {"interests": interests})


def signup(request):
    if request.user.is_authenticated:
        return redirect("agenda:recommendations")
    form = UserCreationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        return redirect("agenda:profile")
    return render(request, "agenda/edit.html", {
        "form": form, "heading": "Создать аккаунт", "submit": "Зарегистрироваться",
    })


@login_required
def profile(request):
    visitor = Visitor.objects.filter(account=request.user).first()
    form = VisitorForm(request.POST if request.method == "POST" else None, instance=visitor)
    if request.method == "POST" and form.is_valid():
        visitor = form.save(commit=False)
        visitor.account = request.user
        visitor.save()
        form.save_m2m()
        messages.success(request, "Профиль сохранён.")
        return redirect("agenda:recommendations")
    return render(request, "agenda/edit.html", {
        "form": form, "heading": "Мои интересы и бюджет", "submit": "Сохранить профиль",
    })


def visit_recommendations(visitor, mode):
    if mode in (Recommendation.Status.SAVED, Recommendation.Status.DISMISSED):
        return Event.objects.filter(
            recommendations__visitor=visitor, recommendations__status=mode,
        ).annotate(score=F("recommendations__score"), state=Value(mode))
    state = visitor.recommendations.filter(event_id=OuterRef("pk")).values("status")[:1]
    return matching_events(visitor).annotate(
        state=Coalesce(Subquery(state), Value(Recommendation.Status.NEW)),
    )


@login_required
def recommendation_list(request):
    visitor = Visitor.objects.filter(account=request.user).first()
    form = RecommendationFilterForm(request.GET)
    events = Event.objects.none()
    if visitor and form.is_valid():
        mode = form.cleaned_data["status"]
        events = apply_filters(visit_recommendations(visitor, mode), form, MATCH_SORT, "score")
    page = Paginator(with_tags(events), 6).get_page(request.GET.get("page"))
    return render(request, "agenda/recommendations.html", {
        "visitor": visitor, "page": page, "form": form,
    })


@login_required
@require_POST
def recommendation_change(request, pk, action):
    visitor = get_object_or_404(Visitor, account=request.user)
    if action == "restore":
        record = get_object_or_404(visitor.recommendations, event_id=pk)
        record.status = Recommendation.Status.NEW
        record.save(update_fields=["status"])
        messages.success(request, "Статус рекомендации сброшен.")
    else:
        status = {"save": Recommendation.Status.SAVED,
                  "dismiss": Recommendation.Status.DISMISSED}.get(action)
        if status is None:
            raise Http404
        event = get_object_or_404(matching_events(visitor), pk=pk)
        Recommendation.objects.update_or_create(
            visitor=visitor, event=event, defaults={"score": event.score, "status": status},
        )
        messages.success(request, "Рекомендация обновлена.")
    return redirect("agenda:recommendations")


def save_event(request, event=None):
    if request.method == "POST":
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            saved_event = form.save()
            messages.success(request, "Мероприятие сохранено.")
            if not saved_event.active and not request.user.has_perm("agenda.change_event"):
                return redirect("agenda:events")
            return redirect(saved_event)
    else:
        form = EventForm(instance=event)
    return render(request, "agenda/edit.html", {
        "form": form, "heading": "Редактирование мероприятия" if event else "Новое мероприятие",
        "submit": "Сохранить мероприятие", "upload": True,
    })


@permission_required("agenda.add_event", raise_exception=True)
def event_create(request):
    return save_event(request)


@permission_required("agenda.change_event", raise_exception=True)
def event_edit(request, pk):
    return save_event(request, get_object_or_404(Event, pk=pk))


def stats(request):
    return render(request, "agenda/stats.html", statistics())


def not_found(request, exception):
    return render(request, "404.html", status=404)
