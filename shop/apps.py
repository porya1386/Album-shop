from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ShopConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "shop"

    def ready(self):
        from .colors import seed_colors

        post_migrate.connect(seed_colors, sender=self)
