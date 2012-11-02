from django.db import models
from django.contrib.auth.models import User

from djeuscan.models import Herd, Maintainer, Package, Category, Overlay


class UserProfile(models.Model):
    EMAIL_SCAN = 1
    EMAIL_WEEKLY = 2
    EMAIL_MONTHLY = 3
    EMAIL_OPTS = (
        (EMAIL_SCAN, 'On updates'),
        (EMAIL_WEEKLY, 'Weekly'),
        (EMAIL_MONTHLY, 'Monthly')
    )

    user = models.OneToOneField(User)
    herds = models.ManyToManyField(Herd)
    maintainers = models.ManyToManyField(Maintainer)
    packages = models.ManyToManyField(Package)
    categories = models.ManyToManyField(Category)
    overlays = models.ManyToManyField(Overlay)

    feed_upstream_info = models.BooleanField(default=True)
    feed_portage_info = models.BooleanField(default=False)
    feed_show_adds = models.BooleanField(default=True)
    feed_show_removals = models.BooleanField(default=True)
    feed_ignore_pre = models.BooleanField(default=False)
    feed_ignore_pre_if_stable = models.BooleanField(default=False)

    email_activated = models.BooleanField(default=True)
    email_every = models.IntegerField(choices=EMAIL_OPTS, default=EMAIL_SCAN)
    email_ignore_pre = models.BooleanField(default=False)
    email_ignore_pre_if_stable = models.BooleanField(default=False)
    last_email = models.DateTimeField(auto_now_add=True)
