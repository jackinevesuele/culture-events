from django.contrib import admin

from .models import Event, Interest, Recommendation, Visitor

admin.site.site_header = "Управление афишей"
admin.site.site_title = "Культурный маршрут"
admin.site.index_title = "Справочники и рекомендации"


class EventRecommendationInline(admin.TabularInline):
    model = Recommendation
    fields = ("visitor", "score", "status")
    readonly_fields = fields
    extra = 0
    can_delete = False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("visitor")

    def has_add_permission(self, request, obj=None):
        return False


class VisitorRecommendationInline(admin.TabularInline):
    model = Recommendation
    fields = ("event", "score", "status")
    readonly_fields = fields
    extra = 0
    can_delete = False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("event")

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ("name", "account", "age", "budget")
    list_filter = ("interests",)
    search_fields = ("name", "account__username")
    ordering = ("name", "pk")
    list_select_related = ("account",)
    autocomplete_fields = ("account",)
    filter_horizontal = ("interests",)
    inlines = (VisitorRecommendationInline,)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "venue", "price", "min_age", "active")
    list_filter = ("active", "date", "interests", "min_age")
    search_fields = ("name", "venue")
    ordering = ("date", "pk")
    date_hierarchy = "date"
    filter_horizontal = ("interests",)
    inlines = (EventRecommendationInline,)


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("visitor", "event", "score", "status")
    list_filter = ("status", "event__date", "event")
    search_fields = ("visitor__name", "event__name")
    ordering = ("-score", "pk")
    list_select_related = ("visitor", "event")
    autocomplete_fields = ("visitor", "event")
