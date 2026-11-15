from datetime import date

from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render

from .models import Event, Interest, Visitor
from .selectors import (
    EVENT_SORT, MATCH_SORT, matching_events, search_events, statistics,
    upcoming_events, with_tags,
)


def home(request):
    events = with_tags(upcoming_events())[:3]
    return render(request, "agenda/home.html", {"events": events})


def event_list(request):
    query = request.GET.get("q", "").strip()
    sort = EVENT_SORT.get(request.GET.get("sort"), EVENT_SORT["date"])
    results = with_tags(search_events(upcoming_events(), query)).order_by(*sort)
    page = Paginator(results, 6).get_page(request.GET.get("page"))
    return render(request, "agenda/events.html", {"events": page, "page": page, "q": query})


def event_detail(request, pk):
    event = get_object_or_404(with_tags(Event.objects.filter(active=True)), pk=pk)
    return render(request, "agenda/event.html", {"event": event})


def interest_list(request):
    interests = Interest.objects.annotate(total=Count("events"))
    return render(request, "agenda/interests.html", {"interests": interests})


def recommendation_list(request):
    visitor = Visitor.objects.filter(pk=request.GET.get("user", "1")).first() \
        if request.GET.get("user", "1").isdecimal() else None
    events = Event.objects.none()
    if visitor:
        on_date = request.GET.get("date", "")
        try:
            start = date.fromisoformat(on_date)
        except ValueError:
            start = None
        interest = request.GET.get("interest", "")
        sort = MATCH_SORT.get(request.GET.get("sort"), MATCH_SORT["score"])
        events = search_events(
            matching_events(visitor), interest=interest if interest.isdecimal() else None,
            start=start,
        ).order_by(*sort)
    page = Paginator(with_tags(events), 6).get_page(request.GET.get("page"))
    return render(request, "agenda/recommendations.html", {
        "events": page, "page": page, "visitor": visitor,
    })


def stats(request):
    return render(request, "agenda/stats.html", statistics())


def not_found(request, exception):
    return render(request, "404.html", status=404)
