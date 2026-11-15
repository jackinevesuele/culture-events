from datetime import timedelta

from django.test import TestCase
from django.utils.timezone import localdate

from .models import Event, Interest, Visitor
from .selectors import matching_events, with_tags


class QueryTests(TestCase):
    def test_match_cards_use_two_queries_regardless_of_count(self):
        tag = Interest.objects.create(name="Кино")
        visitor = Visitor.objects.create(name="Мария", budget=1000, age=20)
        visitor.interests.add(tag)
        for i in range(8):
            event = Event.objects.create(
                name=f"Сеанс {i}", price=i*100, date=localdate()+timedelta(days=i),
            )
            event.interests.add(tag)

        with self.assertNumQueries(2):
            items = list(with_tags(matching_events(visitor)))
            rendered = [(event.score, event.tag_list[0].name) for event in items]

        self.assertEqual(rendered, [(1, "Кино")] * 8)
