from datetime import timedelta
from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.timezone import localdate
from PIL import Image

from .models import Event, Interest, Recommendation, Visitor


class Workflows(TestCase):
    @classmethod
    def setUpTestData(cls):
        accounts = get_user_model().objects
        cls.user = accounts.create_user("visitor")
        cls.other = accounts.create_user("other")
        cls.editor = accounts.create_superuser("editor", password="ExampleOnly!2026")
        cls.music = Interest.objects.create(name="Музыка")
        cls.art = Interest.objects.create(name="Искусство")
        cls.visitor = Visitor.objects.create(
            account=cls.user, name="Посетитель", age=16, budget=700,
        )
        cls.visitor.interests.set([cls.music, cls.art])
        cls.today = localdate()
        cls.event = cls.add_event("Джаз и живопись", 550, [cls.music, cls.art])
        cls.free = cls.add_event("Открытый концерт", 0, [cls.music])
        cls.add_event("Дорого", 701, [cls.music])
        cls.add_event("18+", 300, [cls.music], min_age=18)
        cls.add_event("Архив", 300, [cls.music], active=False)
        cls.add_event("Вчера", 200, [cls.music], date=cls.today-timedelta(days=1))

    @classmethod
    def add_event(cls, title, price, interests, **overrides):
        values = {"date": cls.today, "min_age": 0, **overrides}
        event = Event.objects.create(name=title, price=price, **values)
        event.interests.set(interests)
        return event

    def test_public_catalogue_validates_and_searches_cyrillic(self):
        url = reverse("agenda:events")
        response = self.client.get(url, {
            "q": "ДЖАЗ", "interest": self.art.pk, "price": "550", "sort": "price",
        })
        self.assertContains(response, self.event.name)
        self.assertNotContains(response, self.free.name)
        response = self.client.get(url, {"price": "-1", "start": "вчера", "sort": "invalid"})
        self.assertEqual(set(response.context["form"].errors), {"price", "start", "sort"})
        self.assertEqual(len(response.context["page"]), 0)

    def test_pagination_preserves_filters(self):
        for index in range(7):
            self.add_event(f"Показ {index}", 0, [self.music])
        response = self.client.get(reverse("agenda:events"), {"q": "Показ", "sort": "price"})
        self.assertEqual(len(response.context["page"]), 6)
        self.assertContains(response, "page=2")
        self.assertContains(response, "sort=price")
        response = self.client.get(reverse("agenda:events"), {
            "q": "Показ", "sort": "price", "page": 2,
        })
        self.assertEqual(len(response.context["page"]), 1)

    def test_recommendations_rank_and_isolate_user_state(self):
        url = reverse("agenda:recommendations")
        self.assertRedirects(self.client.get(url), reverse("agenda:login") + "?next=" + url)
        self.client.force_login(self.user)
        page = self.client.get(url).context["page"]
        self.assertEqual([(e.pk, e.score) for e in page], [(self.event.pk, 2), (self.free.pk, 1)])
        save = reverse("agenda:recommendation_change", args=(self.event.pk, "save"))
        self.assertEqual(self.client.get(save).status_code, 405)
        self.assertRedirects(self.client.post(save), url)
        self.assertEqual([e.pk for e in self.client.get(url, {"status": "saved"}).context["page"]],
                         [self.event.pk])
        dismiss = reverse("agenda:recommendation_change", args=(self.event.pk, "dismiss"))
        self.assertRedirects(self.client.post(dismiss), url)
        self.assertNotContains(self.client.get(url), self.event.name)
        self.assertContains(self.client.get(url, {"status": "dismissed"}), self.event.name)
        restore = reverse("agenda:recommendation_change", args=(self.event.pk, "restore"))
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(restore).status_code, 404)
        self.client.force_login(self.user)
        self.assertRedirects(self.client.post(restore), url)
        self.assertContains(self.client.get(url), self.event.name)
        self.assertEqual(self.visitor.recommendations.get().status, Recommendation.Status.NEW)

    def test_profile_registration_and_validation(self):
        signup = reverse("agenda:signup")
        profile = reverse("agenda:profile")
        url = reverse("agenda:recommendations")
        password = "FirstVisit!2468"
        self.assertRedirects(self.client.post(signup, {
            "username": "newvisitor", "password1": password, "password2": password,
        }), profile)
        self.assertContains(self.client.get(url), "Заполнить профиль")
        response = self.client.post(profile, {"name": "Анна", "age": 121, "budget": -1})
        self.assertEqual(set(response.context["form"].errors), {"age", "budget"})
        self.assertRedirects(self.client.post(profile, {
            "name": "Анна", "age": 22, "budget": "550.50", "interests": [self.music.pk],
        }), url)
        self.assertContains(self.client.get(url), self.event.name)

    def test_editor_create_edit_and_archive_with_poster(self):
        create = reverse("agenda:event_create")
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(create).status_code, 403)
        self.client.force_login(self.editor)
        data = {"name": "Новый показ", "date": self.today.isoformat(),
                "venue": "Зал", "price": "100", "min_age": 6,
                "interests": [self.music.pk], "active": "on"}
        image = BytesIO()
        Image.new("RGB", (28, 28), "#4e2850").save(image, "PNG")
        with TemporaryDirectory() as media, self.settings(MEDIA_ROOT=media):
            response = self.client.post(create, {
                **data, "poster": SimpleUploadedFile("bad.png", b"invalid", "image/png"),
            })
            self.assertIn("poster", response.context["form"].errors)
            self.assertFalse(Event.objects.filter(name=data["name"]).exists())
            response = self.client.post(create, {
                **data, "poster": SimpleUploadedFile("test.png", image.getvalue(), "image/png"),
            })
            event = Event.objects.get(name=data["name"])
            self.assertRedirects(response, event.get_absolute_url())
            self.assertTrue(event.poster.storage.exists(event.poster.name))
            self.assertContains(self.client.get(event.get_absolute_url()), event.poster.url)
            edit = reverse("agenda:event_edit", args=[event.pk])
            self.assertRedirects(self.client.post(edit, {**data, "active": ""}),
                                 event.get_absolute_url())
            event.refresh_from_db()
            self.assertFalse(event.active)
            self.client.logout()
            self.assertEqual(self.client.get(event.get_absolute_url()).status_code, 404)

    def test_rejects_incomplete_event_and_past_publication(self):
        self.client.force_login(self.editor)
        url = reverse("agenda:event_create")
        self.assertIn("name", self.client.post(url, {}).context["form"].errors)
        response = self.client.post(url, {
            "name": "Задним числом", "date": self.today-timedelta(days=1),
            "price": 0, "min_age": 0, "active": "on", "interests": [self.music.pk],
        })
        self.assertIn("date", response.context["form"].errors)

    def test_post_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        url = reverse("agenda:recommendation_change", args=(self.event.pk, "save"))
        self.assertEqual(client.post(url).status_code, 403)
        client.get(reverse("agenda:recommendations"))
        token = client.cookies["csrftoken"].value
        self.assertEqual(client.post(url, {"csrfmiddlewaretoken": token}).status_code, 302)

    def test_admin_statistics_and_custom_404(self):
        self.assertContains(self.client.get(reverse("agenda:stats")), "События по интересам")
        self.client.force_login(self.editor)
        for model in ("event", "interest", "visitor", "recommendation"):
            admin_url = reverse(f"admin:agenda_{model}_changelist")
            self.assertEqual(self.client.get(admin_url).status_code, 200)
        with patch("django.conf.settings.DEBUG", False):
            response = self.client.get("/unknown/")
            self.assertContains(response, "Страница не найдена", status_code=404)
