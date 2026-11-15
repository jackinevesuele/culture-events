from django.urls import include, path

urlpatterns = [path("", include("agenda.urls"))]
handler404 = "agenda.views.not_found"
