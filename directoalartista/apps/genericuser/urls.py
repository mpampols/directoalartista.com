from django.conf.urls import *

from django.views.generic import TemplateView

from directoalartista.apps.genericuser import ragbackend


urlpatterns = patterns(
    '',

    # Django allauth
    url(r'^accounts/', include('allauth.urls')),

    # Registration module backends
    url(r'^', include('registration.backends.default.urls')),

    # Register
    #url(r'^register/$', RegistrationView.as_view(), name='registration_register'),
    url(r'^register/closed/$', TemplateView.as_view(template_name='registration/registration_closed.html'),
        name='registration_disallowed'), (r'', include('registration.auth_urls')),

    # Activate
    #url(r'^activate/(?P<activation_key>\w+)/$', ActivationView.as_view(), name='registration_activate'),
    url(r'^activate/complete/$', TemplateView.as_view(template_name='registration/activation_complete.html'),
        name='registration_activation_complete'),

    # Password reset
    url(r'^password_reset/$', 'directoalartista.apps.genericuser.views.password_reset', {
        'template_name': 'password_reset_form.html'}),
    url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done', {
        'template_name': 'password_reset_done.html'}),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm', {'template_name': 'password_reset_confirm.html'}
    ),
    url(r'^reset/done/$',
        'django.contrib.auth.views.password_reset_complete', {'template_name': 'password_reset_complete.html'}
    ),
)
