
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("short_body", "user", "product", "created_at")
    list_filter = ("created_at",)
    search_fields = ("body", "user__username", "product__title")
    date_hierarchy = "created_at"
    raw_id_fields = ("product", "user")
    list_select_related = ("user", "product")
    # the default "Delete selected" action is on: moderators can remove many comments at once

    @admin.display(description=_("comment"))
    def short_body(self, obj):
        return obj.body if len(obj.body) <= 60 else obj.body[:57] + "..."
