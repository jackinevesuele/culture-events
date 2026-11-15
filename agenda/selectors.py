from django.db.models import CharField, Count, Func, Max, Min, Prefetch, Q
from django.utils.timezone import localdate

from .models import Event, Interest, Recommendation, Visitor

EVENT_SORT = {
    "date": ("date", "id"),
    "price": ("price", "date", "id"),
    "name": ("name", "id"),
}
MATCH_SORT = {
    "score": ("-score", "price", "date", "id"),
    **EVENT_SORT,
}


def with_tags(events):
    return events.prefetch_related(Prefetch("interests", to_attr="tag_list"))


def upcoming_events():
    return Event.objects.filter(active=True, date__gte=localdate())


def search_events(queryset, query="", interest=None, start=None, price=None):
    if query:
        queryset = queryset.alias(
            folded_name=Func("name", function="CASEFOLD", output_field=CharField()),
            folded_venue=Func("venue", function="CASEFOLD", output_field=CharField()),
        ).filter(Q(folded_name__contains=query.casefold())
                 | Q(folded_venue__contains=query.casefold()))
    if interest:
        queryset = queryset.filter(interests=interest)
    if start:
        queryset = queryset.filter(date__gte=start)
    if price is not None:
        queryset = queryset.filter(price__lte=price)
    return queryset


def matching_events(visitor, *, include_dismissed=False):
    matches = upcoming_events().filter(
        min_age__lte=visitor.age, price__lte=visitor.budget,
    ).annotate(
        score=Count("interests", filter=Q(interests__in=visitor.interests.all()), distinct=True),
    ).filter(score__gt=0)
    if not include_dismissed:
        dismissed = visitor.recommendations.filter(
            status=Recommendation.Status.DISMISSED,
        ).values("event_id")
        matches = matches.exclude(pk__in=dismissed)
    return matches.order_by(*MATCH_SORT["score"])


def statistics():
    events = upcoming_events()
    return {
        "events": events.count(),
        "visitors": Visitor.objects.count(),
        "saved": Recommendation.objects.filter(status=Recommendation.Status.SAVED).count(),
        "prices": events.aggregate(minimum=Min("price"), maximum=Max("price")),
        "interests": Interest.objects.annotate(total=Count(
            "events", filter=Q(events__active=True, events__date__gte=localdate()),
        )).order_by("-total", "name"),
    }
