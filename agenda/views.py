from datetime import date

from django.http import Http404, HttpResponse
from django.urls import reverse
from django.utils.html import escape, format_html_join

from .legacy import catalogue, enrich


def page(title, content, status=200):
    links = [("home", "Главная"), ("events", "Афиша"),
             ("interests", "Интересы"), ("recommendations", "Рекомендации")]
    nav = format_html_join(" ", '<a href="{}">{}</a>',
                           ((reverse("agenda:" + n), text) for n, text in links))
    return HttpResponse(
        f'<!doctype html><html lang="ru"><meta charset="utf-8">'
        f'<title>{escape(title)}</title>'
        '<link rel="stylesheet" href="https://cdn.jsdelivr.net/'
        'npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">'
        '<body class="container py-4" style="max-width:920px">'
        f'<nav class="d-flex gap-3 mb-4">{nav}</nav>'
        f'<main><h1>{escape(title)}</h1>{content}</main></body></html>',
        status=status,
    )


def event_links(events):
    return format_html_join("", '<p><a href="{}">{}</a> · {} · {} ₽</p>',
                            ((reverse("agenda:event", args=[e["id"]]),
                              e["name"], e["date"], e["price"]) for e in events))


def home(request):
    return page("Культурная афиша", "<p>Подбор культурных мероприятий.</p>"
                + event_links(catalogue()["events"][:3]))


def event_list(request):
    return page("Афиша", event_links(catalogue()["events"]))


def event_detail(request, pk):
    data = enrich(catalogue())
    event = next((e for e in data["events"] if e["id"] == pk), None)
    if event is None:
        raise Http404
    tags = ", ".join(i["name"] for i in event["interests"])
    return page(event["name"], f'<p>{escape(tags)}. {escape(event["date"])}, '
                f'{escape(event["price"])} ₽, {event["min_age"]}+.</p>')


def interest_list(request):
    items = format_html_join("", "<li>{}</li>",
                             ((i["name"],) for i in catalogue()["interests"]))
    return page("Интересы", f"<ul>{items}</ul>")


def recommendation_list(request):
    data = catalogue()
    visitor = data["users"][0]
    events = []
    for event in data["events"]:
        shared = set(event["interest_ids"]) & set(visitor["interest_ids"])
        if (shared and event["active"] and event["date"] >= date.today().isoformat()
                and event["min_age"] <= visitor["age"]
                and event["price"] <= visitor["budget"]):
            events.append((len(shared), event))
    events.sort(key=lambda pair: (-pair[0], pair[1]["price"]))
    return page("Рекомендации", event_links(e for _, e in events)
                or "<p>Пока нет подходящих мероприятий.</p>")


def not_found(request, exception):
    return page("Страница не найдена", "<p>Проверьте адрес.</p>", status=404)
