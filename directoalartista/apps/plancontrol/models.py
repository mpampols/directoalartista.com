from django.db import models

from django.contrib.auth.models import User

from django.conf import settings
User = settings.AUTH_USER_MODEL

from datetime import datetime, timedelta

from directoalartista.apps.genericuser.models import GenericUser

from django.contrib.auth import get_user_model
#User = get_user_model()



class ArtistPlan(models.Model):
    # Fields for Artist user
    ARTIST_PLANS = (
        ("4", "Free"),
        ("3", "Starter"),
        ("2", "Unlimited")
    )

    user = models.ForeignKey(User)
    new_plan = models.CharField(max_length=15, blank=True, choices=ARTIST_PLANS)
    subscr_id = models.CharField(max_length=20, blank=True, null=True)
    change_date = models.DateField(auto_now_add=True)
    expiration_date = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return self.user.email