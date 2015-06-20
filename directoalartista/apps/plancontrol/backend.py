# -*- coding: utf-8 -*-
from django.conf import settings
from datetime import datetime, date

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from premailer import transform
from django.core.mail import EmailMultiAlternatives

from directoalartista.apps.plancontrol.models import ArtistPlan
from directoalartista.apps.artistprofile.models import ArtistProfile, ArtistVideo, ArtistPicture


def change_plan(user, new_plan):
    '''
    Change plan now
    '''
    if int(user.artist_plan) < int(new_plan):
        limits = settings.USER_LIMITS
        artist_profile = ArtistProfile.objects.filter(proprietary_user=user)

        if new_plan == '3': # starter
            for i in artist_profile:
                obj = i.secondary_categories.all()
                count = obj.count()
                for o in obj:
                    if count > limits['artistprofile_max_secondarycategories_3']:
                        i.secondary_categories.remove(o)
                        count = count - 1

                obj = i.event_type.all()
                count = obj.count()
                for o in obj:
                    if count > limits['artistprofile_max_eventtypes_3']:
                        i.event_type.remove(o)
                        count = count - 1

                obj = i.provinces.all()
                count = obj.count()
                for o in obj:
                    if count > limits['artistprofile_max_provinces_3']:
                        i.provinces.remove(o)
                        count = count - 1

                i.save()

                obj = ArtistPicture.objects.filter(artistprofile=i)
                count = obj.count()
                for o in obj:
                    if count > limits['artistprofile_max_pictures_3'] and not o.is_main:
                        o.delete()
                        count = count - 1

                obj = ArtistVideo.objects.filter(artistprofile=i)
                count = obj.count()
                for o in obj:
                    if count > limits['artistprofile_max_videos_3']:
                        o.delete()
                        count = count - 1

        elif new_plan == '4': # free
            for i in artist_profile:
                i.secondary_categories.clear()

                obj = i.event_type.all()
                count = obj.count()
                for o in obj:
                    if count > limits['artistprofile_max_eventtypes_4']:
                        i.event_type.remove(o)
                        count = count - 1

                obj = i.provinces.all()
                count = obj.count()
                for o in obj:
                    if count > limits['artistprofile_max_provinces_4']:
                        i.provinces.remove(o)
                        count = count - 1

                i.save()

                obj = ArtistPicture.objects.filter(artistprofile=i)
                count = obj.count()
                for o in obj:
                    if count > limits['artistprofile_max_pictures_4'] and not o.is_main:
                        o.delete()
                        count = count - 1

                obj = ArtistVideo.objects.filter(artistprofile=i)
                count = obj.count()
                for o in obj:
                    if count > limits['artistprofile_max_videos_4']:
                        o.delete()
                        count = count - 1

    plan = ArtistPlan()
    plan.user = user
    plan.change_date = datetime.now()
    plan.new_plan = new_plan

    user = plan.user
    user.artist_plan = plan.new_plan

    user.save()
    plan.save()

    if user.newsletter_subscription:
        user.setUserNewsletterSubscription('artist', new_plan)

    return plan

def free_change_plan(user, new_plan):
    '''
    Called if new plan is free
    '''
    if user.artist_plan == '3' or user.artist_plan == '2':
        old_plan = ArtistPlan.objects.filter(user=user).exclude(subscr_id__isnull=True).exclude(subscr_id__exact='')
        try:
            old_plan = old_plan.order_by('id').reverse()[0]
            # if new_plan is free
            if new_plan == '4':
                return paypal_cancel_subscription(old_plan)
        except:
            pass

    return change_plan(user,new_plan)

def paypal_change_plan(invoice, invoiceitem, ipn_obj):
    '''
    Called if new plan is starter or unlimited
    '''
    old_plan = ArtistPlan.objects.filter(user=invoice.proprietary_member).order_by('id').reverse()[0]

    if old_plan.subscr_id != ipn_obj.subscr_id:
        if old_plan.new_plan == '3' or old_plan.new_plan == '2':
            paypal_cancel_subscription(old_plan)

    if ipn_obj.item_number == 'SU-PLA1':
        new_plan = '3'
    elif ipn_obj.item_number == 'SU-DIA1':
        new_plan = '2'
    else:
        return False

    user = invoice.proprietary_member
    plan = change_plan(user,new_plan)
    plan.subscr_id = ipn_obj.subscr_id
    plan.save()

    return True

def paypal_subscription_canceled(sender, **kwargs):
    ipn_obj = sender
    plan = ArtistPlan.objects.filter(subscr_id=ipn_obj.subscr_id).order_by('id').reverse()[0]
    last_plan = ArtistPlan.objects.filter(user=plan.user).order_by('id').reverse()[0]

    # If the plan canceled is the same of last plan movement, this plan is marked for change to free when expire
    if plan == last_plan:
        today = date.today()
        year = today.year
        day = plan.change_date.day
        if today.day < day:
            month = today.month
        else:
            month = today.month + 1

        # Add 1 month
        if month == 13:
            year += 1
            month = 1

        if day == 31:
            if month == 2:
                day = 28
            elif month == 4 or month == 6 or month == 9 or month == 11:
                day = 30

        plan.expiration_date = date(year, month, day)
        plan.save()

    return True

def paypal_cancel_subscription(plan):
    '''
    Call Paypal for cancel subscription payment
    '''
    import urllib
    import urllib2

    form_fields = {
            "METHOD": "ManageRecurringPaymentsProfileStatus",
            "PROFILEID": plan.subscr_id,
            "ACTION": "cancel",
            "USER": settings.PAYPAL_API_USERNAME,
            "PWD": settings.PAYPAL_API_PASSWORD,
            "SIGNATURE": settings.PAYPAL_API_SIGNATURE,
            "VERSION": "54.0"
    }

    form_data = urllib.urlencode(form_fields)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    req = urllib2.Request(settings.PAYPAL_API_URL, form_data, headers)
    response = urllib2.urlopen(req).read()
    response_tokens = {}
    for token in response.split('&'):
        response_tokens[token.split("=")[0]] = token.split("=")[1]
    for key in response_tokens.keys():
            response_tokens[key] = urllib.unquote(response_tokens[key])

    # ACK return 'Failure' or 'Success'
    return response_tokens['ACK']

def paypal_subscription_eot(sender, **kwargs):
    '''
    Paypal signal when plan expire, return to free and send mail to user
    '''
    ipn_obj = sender

    plan = ArtistPlan.objects.filter(subscr_id=ipn_obj.subscr_id).order_by('id').reverse()[0]
    last_plan = ArtistPlan.objects.filter(user=plan.user).order_by('id').reverse()[0]

    # If the plan canceled is the same of last plan movement, this plan is marked for change to free when expire
    if plan == last_plan:
        user = plan.user
        change_plan(user, '4') # free

        subject, from_email = 'Plan actualizado a Gratuito', 'Directo al Artista <noreply@directoalartista.com>'
        message = render_to_string('email/free_plan_return.html', {
            'user': user,
        })

        html_content = render_to_string('email/global/template.html', {
            'email_title': 'Plan actualizado a Gratuito',
            'email_content': message,
        })

        html_content = transform(html_content)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    return True
