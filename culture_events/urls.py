from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("agenda.urls")),
]
handler404 = "agenda.views.not_found"
