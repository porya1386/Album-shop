from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Comment


class CommentAdminForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = "__all__"

    def clean(self):
        data = super().clean()
        if bool(data.get("product")) == bool(data.get("sculpture")):
            raise forms.ValidationError(
                _("Choose either a painting or a sculpture (not both, not none).")
            )
        return data


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    form = CommentAdminForm
    list_display = ("short_body", "user", "target_title", "created_at")
    list_filter = ("created_at",)
    search_fields = ("body", "user__username",
                     "product__title", "sculpture__title")
    date_hierarchy = "created_at"
    raw_id_fields = ("product", "sculpture", "user")
    list_select_related = ("user", "product", "sculpture")
    # the default "Delete selected" action is on: moderators can remove many comments at once

    @admin.display(description=_("comment"))
    def short_body(self, obj):
        return obj.body if len(obj.body) <= 60 else obj.body[:57] + "..."

    @admin.display(description=_("Product"))
    def target_title(self, obj):
        target = obj.target
        return target.title if target else "-"
