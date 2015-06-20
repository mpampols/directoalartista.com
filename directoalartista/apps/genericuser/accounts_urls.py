from django.conf.urls import *

from django.views.generic import TemplateView

from directoalartista.apps.transaction import views as TransactionViews
from directoalartista.apps.myaccount import views as MyAccountView

from directoalartista.apps.genericuser.views import ArtistCustomRegistrationView, \
    AgencyCustomRegistrationView, PromoterCustomRegistrationView, resend_activation_email

from directoalartista.apps.genericuser.forms import GenericUserCustomRegistrationFormArtist, \
    GenericUserCustomRegistrationFormAgency, GenericUserCustomRegistrationFormPromoter


# /accounts

urlpatterns = patterns('',
    # Profile
    url(r'^profile/$', MyAccountView.profile, name='myaccount'),
    url(r'^profile/edit/', MyAccountView.edit_profile, name='myaccount'),
    url(r'^profile/disable/', MyAccountView.disable_user, name='disableaccount'),

    # Login / Logout
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'registration/login.html'}),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'registration/logout.html'}),

    # Password change
    url(r'^password_change/$', 'django.contrib.auth.views.password_change', {
        'template_name': 'password_change_form.html'}),
    url(r'^password_change/done/$', 'django.contrib.auth.views.password_change_done', {
        'template_name': 'password_change_done.html'}),

    # Resend activation email
    url(r'^resend/$', 'directoalartista.apps.genericuser.views.resend_activation_email'),

    # Register artist
    #url(r'^artist/register/$', ArtistCustomRegistrationView.as_view(
    #    form_class=GenericUserCustomRegistrationFormArtist), name='registration_artist_register'
    #),
    url(r'^artist/register/complete', TemplateView.as_view(
        template_name='registration/registration_complete_artist.html'), name='registration_artist_complete'
    ),
    url(r'^artist/register/not_activated', TemplateView.as_view(
        template_name='registration/registration_not_activated_artist.html'), name='registration_artist_error'
    ),
    url(r'^artist/register/already_activated', TemplateView.as_view(
        template_name='registration/registration_already_activated_artist.html'), name='registration_artist_error'
    ),

    # Register agency
    #url(r'^agency/register/$', AgencyCustomRegistrationView.as_view(
    #    form_class=GenericUserCustomRegistrationFormAgency), name='registration_agency_register'
    #),
    url(r'^agency/register/complete', TemplateView.as_view(
        template_name='registration/registration_complete_agency.html'), name='registration_agency_complete'
    ),
    url(r'^agency/register/not_activated', TemplateView.as_view(
        template_name='registration/registration_not_activated_agency.html'), name='registration_artist_error'
    ),
    url(r'^agency/register/already_activated', TemplateView.as_view(
        template_name='registration/registration_already_activated_agency.html'), name='registration_artist_error'
    ),

    # Register promoter
    #url(r'^promoter/register/$', PromoterCustomRegistrationView.as_view(
    #    form_class=GenericUserCustomRegistrationFormPromoter), name='registration_promoter_register'
    #),
    url(r'^promoter/register/complete', TemplateView.as_view(
        template_name='registration/registration_complete_promoter.html'), name='registration_promoter_complete'
    ),
    url(r'^promoter/register/not_activated', TemplateView.as_view(
        template_name='registration/registration_not_activated_promoter.html'), name='registration_artist_error'
    ),
    url(r'^promoter/register/already_activated', TemplateView.as_view(
        template_name='registration/registration_already_activated_promoter.html'), name='registration_artist_error'
    ),
)
