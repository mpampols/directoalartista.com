from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from directoalartista.apps.genericuser.models import GenericUser
from directoalartista.apps.plancontrol.models import ArtistPlan


class ArtistPlanAdmin(admin.ModelAdmin):
    list_display = ('user', 'new_plan', 'change_date', 'subscr_id', 'expiration_date')


admin.site.register(ArtistPlan, ArtistPlanAdmin)