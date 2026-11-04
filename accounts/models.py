from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class CustomUser(AbstractUser):
    # set when the person ticks "I agree to the Terms" on the register form (empty for older / social accounts)
    terms_accepted_at = models.DateTimeField(
        _("Terms accepted at"), null=True, blank=True, editable=False)
