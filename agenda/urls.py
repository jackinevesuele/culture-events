from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "agenda"
urlpatterns = [
    path("", views.home, name="home"),
    path("events/", views.event_list, name="events"),
    path("events/new/", views.event_create, name="event_create"),
    path("events/<int:pk>/", views.event_detail, name="event"),
    path("events/<int:pk>/edit/", views.event_edit, name="event_edit"),
    path("interests/", views.interest_list, name="interests"),
    path("recommendations/", views.recommendation_list, name="recommendations"),
    path("recommendations/<int:pk>/<str:action>/", views.recommendation_change,
         name="recommendation_change"),
    path("stats/", views.stats, name="stats"),
    path("account/signup/", views.signup, name="signup"),
    path("account/login/", auth_views.LoginView.as_view(), name="login"),
    path("account/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("account/profile/", views.profile, name="profile"),
]
