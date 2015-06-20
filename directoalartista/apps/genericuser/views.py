#from registration.backends.default.views import RegistrationView

import hashlib
import random
import datetime

from django.contrib.sites.models import Site
from django.contrib.sites.models import RequestSite
from django.contrib.auth.views import password_reset as django_password_reset
from django.template import Context
from django.shortcuts import render, redirect, render_to_response
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect

from allauth.account.views import SignupView

from directoalartista.apps.genericuser.models import GenericUser
from directoalartista.apps.genericuser.forms import CustomPasswordResetForm
from directoalartista.apps.genericuser.forms import ResendActivationEmailForm
from directoalartista.apps.plancontrol.models import ArtistPlan

from django.db import transaction

from django.contrib.auth import get_user_model
User = get_user_model()


class AgencyCustomRegistrationView(SignupView):
    template_name = "registration/registration_form_agency.html"

    def __init__(self, **kwargs):
        super(AgencyCustomRegistrationView, self).__init__(**kwargs)
        self.return_url= "/accounts/agency/register/complete"

    def register(self, request, **cleaned_data):
        email, password, phone = cleaned_data['email'], cleaned_data['password1'], cleaned_data['phone']
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        users = User.objects.filter(email=email, is_active=0)
        if users.count():
            self.return_url= "/accounts/agency/register/not_activated"
            return 0

        users = User.objects.filter(email=email, is_active=1)
        if users.count():
            self.return_url= "/accounts/agency/register/already_activated"
            return 0

        new_user = RegistrationProfile.objects.create_inactive_user(email, password, phone, site)

        signals.user_registered.send(
            sender=self.__class__, user=new_user, request=request)

        return new_user

    def get_success_url(self, request, user):
        return self.return_url


class PromoterCustomRegistrationView(SignupView):

    template_name = "registration/registration_form_promoter.html"

    def register(self, request, **cleaned_data):
        email, password, phone = cleaned_data['email'], cleaned_data['password1'], cleaned_data['phone']
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        users = User.objects.filter(email=email, is_active=0)
        if users.count():
            self.return_url= "/accounts/promoter/register/not_activated"
            return 0

        users = User.objects.filter(email=email, is_active=1)
        if users.count():
            self.return_url= "/accounts/promoter/register/already_activated"
            return 0

        new_user = RegistrationProfile.objects.create_inactive_user(email, password, phone, site)

        signals.user_registered.send(
            sender=self.__class__, user=new_user, request=request)

        self.return_url= "/accounts/promoter/register/complete"
        return new_user

    def get_success_url(self, request, user):
        return self.return_url


class ArtistCustomRegistrationView(SignupView):

    template_name = "registration/registration_form_artist.html"

    def __init__(self, **kwargs):
        super(ArtistCustomRegistrationView, self).__init__(**kwargs)
        self.return_url= "/accounts/artist/register/complete"

    def register(self, request, **cleaned_data):
        email, password, phone = cleaned_data['email'], cleaned_data['password1'], cleaned_data['phone']
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)

        users = User.objects.filter(email=email, is_active=0)
        if users.count():
            self.return_url= "/accounts/artist/register/not_activated"
            return 0

        users = User.objects.filter(email=email, is_active=1)
        if users.count():
            self.return_url= "/accounts/artist/register/already_activated"
            return 0

        new_user = RegistrationProfile.objects.create_inactive_user(email, password, phone, site)

        signals.user_registered.send(
            sender=self.__class__, user=new_user, request=request)

        return new_user

    def get_success_url(self, request, user):
        return self.return_url


def password_reset(*args, **kwargs):
    """
        Overriding the Email Password Resert Forms Save to be able to send HTML email
    """
    kwargs['password_reset_form'] = CustomPasswordResetForm
    return django_password_reset(*args, **kwargs)

def resend_activation_email(request):

    if not request.user.is_anonymous():
        return HttpResponseRedirect('/')

    context = Context()

    form = None
    if request.method == 'POST':
        form = ResendActivationEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            users = User.objects.filter(email=email, is_active=0)

            if not users.count():
                form._errors["email"] = ("Account for email address is not registered or already activated.")

            for user in users:
                for profile in RegistrationProfile.objects.filter(user=user):
                    if profile.activation_key_expired():
                        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
                        profile.activation_key = hashlib.sha1(salt+user.email).hexdigest()
                        user.date_joined = datetime.datetime.now()
                        user.save()
                        profile.save()

                    if Site._meta.installed:
                        site = Site.objects.get_current()
                    else:
                        site = RequestSite(request)

                    profile.send_activation_email(site)

                    context.update({"form" : form})
                    return render(request, 'registration/resend_activation_email_done.html', context)

    if not form:
        form = ResendActivationEmailForm()

    context.update({"form" : form})
    return render(request, 'registration/resend_activation_email_form.html', context)
