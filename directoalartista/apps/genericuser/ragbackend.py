# -*- coding: utf-8 -*-
from django.utils.text import slugify
from forms import *
import hashlib

from django.dispatch import receiver
from django.contrib.auth import login

from directoalartista.apps.genericuser.models import GenericUser
from directoalartista.apps.genericuser.views import ArtistCustomRegistrationView, AgencyCustomRegistrationView, \
    PromoterCustomRegistrationView
from directoalartista.apps.plancontrol.backend import change_plan

def user_created(sender, user, request, **kwargs):

    if (sender == ArtistCustomRegistrationView):
        form = GenericUserCustomRegistrationFormArtist(request.POST)
        user.first_name = form.data['first_name']
        user.last_name = form.data['last_name']
        user.phone = form.data['phone']
        user.dni = form.data['dni']
        user.address = form.data['address']
        user.postal_code = form.data['postal_code']
        user.city = form.data['city']
        user.province = form.data['province']
        user.slug = slugify(unicode(form.data['first_name'] + "-" + form.data['last_name'] + "-" + str(hashlib.md5(form.data['dni']).hexdigest())[:5]))
        user.user_type = 'A'
        user.artist_plan = '4' # free
        if ('newsletter_subscription' in form.data):
            user.newsletter_subscription = True
        user.save()

    if (sender == PromoterCustomRegistrationView):
        form = GenericUserCustomRegistrationFormPromoter(request.POST)
        user.first_name = form.data['first_name']
        user.last_name = form.data['last_name']
        user.phone = form.data['phone']
        user.dni = form.data['dni']
        user.address = form.data['address']
        user.postal_code = form.data['postal_code']
        user.city = form.data['city']
        user.province = form.data['province']
        user.user_type = 'P'
        user.promoter_room_or_event_name = form.data['promoter_room_or_event_name']
        user.promoter_company_name = form.data['promoter_company_name']
        user.promoter_cif = form.data['promoter_cif']
        user.promoter_additional_info = form.data['promoter_additional_info']
        if ('newsletter_subscription' in form.data):
            user.newsletter_subscription = True
        user.save()

    if (sender == AgencyCustomRegistrationView):
        form = GenericUserCustomRegistrationFormAgency(request.POST)
        user.first_name = form.data['first_name']
        user.last_name = form.data['last_name']
        user.phone = form.data['phone']
        user.dni = form.data['dni']
        user.address = form.data['address']
        user.postal_code = form.data['postal_code']
        user.city = form.data['city']
        user.province = form.data['province']
        user.user_type = 'G'
        user.artist_plan = '4'
        user.agency_name = form.data['agency_name']
        user.agency_company_name = form.data['agency_company_name']
        user.agency_cif = form.data['agency_cif']
        user.agency_additional_info = form.data['agency_additional_info']
        if ('newsletter_subscription' in form.data):
            user.newsletter_subscription = True
        user.save()


#@receiver(user_activated)
def on_activation(sender, user, request, **kwargs):
    """
    1. Override save method to add the mailchimp subscription
    2. If agency, send email to admin
    3. Logs in the user after activation
    """
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    from premailer import transform
    from django.core.mail import EmailMultiAlternatives

    user.backend = 'django.contrib.auth.backends.ModelBackend'

    user_types = {"A": "artist",
                  "P": "promoter",
                  "G": "agency"}
    user_type = user_types[user.user_type]
    if user_type == 'artist':
        user_plan = '4'
    else:
        user_plan = ""
    user.setUserNewsletterSubscription(user_type, user_plan)

    if user.user_type == 'G':
        subject, from_email = 'DA admin - New agency registered', 'Directo al Artista <noreply@directoalartista.com>'
        message = render_to_string('email/agency_actived_email.html', {
            'user': user,
        })

        html_content = render_to_string('email/global/template.html', {
            'email_title': 'New agency registered',
            'email_content': message,
        })

        html_content = transform(html_content)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, ['info@directoalartista.com'])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
    elif user.user_type == 'A':
        change_plan(user, 4) # free

    login(request, user)