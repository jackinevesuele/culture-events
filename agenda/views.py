from datetime import date

from django.http import Http404
from django.shortcuts import render

from .legacy import catalogue, enrich


def home(request):
    data = enrich(catalogue())
    return render(request, "agenda/home.html", {"events": data["events"][:3]})


def event_list(request):
    data = enrich(catalogue())
    query = request.GET.get("q", "").strip()
    events = [e for e in data["events"] if query.casefold() in e["name"].casefold()]
    return render(request, "agenda/events.html", {"events": events, "q": query})


def event_detail(request, pk):
    data = enrich(catalogue())
    event = next((e for e in data["events"] if e["id"] == pk), None)
    if event is None:
        raise Http404
    return render(request, "agenda/event.html", {"event": event})


def interest_list(request):
    return render(request, "agenda/interests.html",
                  {"interests": catalogue()["interests"]})


def recommendation_list(request):
    data = enrich(catalogue())
    visitor = data["users"][0]
    events = []
    for event in data["events"]:
        shared = set(event["interest_ids"]) & set(visitor["interest_ids"])
        if (shared and event["active"] and event["date"] >= date.today().isoformat()
                and event["min_age"] <= visitor["age"]
                and event["price"] <= visitor["budget"]):
            events.append((len(shared), event))
    events.sort(key=lambda pair: (-pair[0], pair[1]["price"]))
    return render(request, "agenda/recommendations.html",
                  {"events": [event for _, event in events]})


def not_found(request, exception):
    return render(request, "404.html", status=404)
