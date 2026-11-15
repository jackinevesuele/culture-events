from datetime import date

from django.http import Http404
from django.shortcuts import render

from . import sql_catalogue as catalogue


def home(request):
    events = catalogue.events("available_events", date.today().isoformat())
    return render(request, "agenda/home.html", {"events": events[:3]})


def event_list(request):
    query = request.GET.get("q", "").strip()
    events = catalogue.events("search_events", query)
    return render(request, "agenda/events.html", {"events": events, "q": query})


def event_detail(request, pk):
    event = next((e for e in catalogue.events("events") if e["id"] == pk), None)
    if event is None:
        raise Http404
    return render(request, "agenda/event.html", {"event": event})


def interest_list(request):
    return render(request, "agenda/interests.html", {"interests": catalogue.interests()})


def recommendation_list(request):
    events = catalogue.events("matching_events", 1, date.today().isoformat())
    return render(request, "agenda/recommendations.html", {"events": events})


def not_found(request, exception):
    return render(request, "404.html", status=404)
