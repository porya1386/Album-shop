from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_moderator_group(sender, **kwargs):
    """After every migrate: make sure the group "Moderator" exists and can manage blog posts."""
    from django.contrib.auth.models import Group, Permission

    group, _ = Group.objects.get_or_create(name="Moderator")
    perms = Permission.objects.filter(
        content_type__app_label="blogs", content_type__model="post"
    )
    group.permissions.add(*perms)


class BlogsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "blogs"
    verbose_name = "Blog"

    def ready(self):
        post_migrate.connect(create_moderator_group, sender=self)
