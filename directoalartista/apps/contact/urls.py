from django.conf.urls import patterns
from django.conf.urls import url
from django.views.generic import TemplateView

from directoalartista.apps.contact import views


urlpatterns = patterns(
    '',
    url(
        r'^$',
        views.contact,
        name='contact_form'
    ),
    url(
        r'^sent/$',
        TemplateView.as_view
        (
            template_name='contact_form_sent.html'
        ),
        name='contact_form_sent'
    )
)
