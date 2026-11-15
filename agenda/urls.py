from django.urls import path

from . import views

app_name = "agenda"
urlpatterns = [
    path("", views.home, name="home"),
    path("events/", views.event_list, name="events"),
    path("events/<int:pk>/", views.event_detail, name="event"),
    path("interests/", views.interest_list, name="interests"),
    path("recommendations/", views.recommendation_list, name="recommendations"),
    path("stats/", views.stats, name="stats"),
]
