# -*- coding: utf-8 -*-
from django.shortcuts import render, render_to_response
from unidecode import unidecode
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.template import Template, context, RequestContext
from django.views.decorators.http import require_GET
from django.http import HttpResponseRedirect, Http404

from paypal.standard.pdt.models import PayPalPDT
from paypal.standard.pdt.forms import PayPalPDTForm

from directoalartista.apps.transaction.models import TransactionContact, TransactionContactItem,\
    TransactionSubscription, TransactionSubscriptionItem
from directoalartista.apps.invoicing.models import Invoice, InvoiceItem
from directoalartista.apps.invoicing.backend import validate_payment
from directoalartista.apps.artistprofile.models import ArtistProfile, ArtistProfileUrlHistory, ArtistCategory


def contact_artist(request, category_url, artist_profile_url):
    try:
        artist_profile = ArtistProfile.objects.get(slug=artist_profile_url)
    except ArtistProfile.DoesNotExist:
        # Before raise a 404 error we can try to locate the user by it's slug and send a
        # 302 redirent to the browser, also Google. To ensure that the redirect is to the correct profile
        # we'll also check the first hash chars
        try:
            artist_profile_url_history = ArtistProfileUrlHistory.objects.filter(slug=artist_profile_url).latest()
            found_artist_profile = ArtistProfile.objects.get(id=artist_profile_url_history.artistprofile_id)
            found_artist_category = ArtistCategory.objects.get(id=found_artist_profile.category_id)
            return HttpResponseRedirect(
                settings.BASE_URL + '/catalog/' + str(found_artist_category.slug) + '/' + found_artist_profile.slug +\
                '/contact'
            )
        except ArtistProfileUrlHistory.DoesNotExist:
            raise Http404

    if request.user.is_anonymous():
        messages.warning(request, "Date de alta gratuítamente para contactar con artistas.")
        return HttpResponseRedirect('/accounts/promoter/register/')
    elif artist_profile.is_vip:
        if request.user.user_type == 'A':
            messages.warning(request, "Para contactar con artitas VIP, tienes que ser promotor o agencia.")
            return HttpResponseRedirect('/catalog/' + category_url + '/' + artist_profile_url)
        elif request.user.user_type == 'G' and not request.user.agency_validated:
            messages.warning(request, "Estás en proceso de validación, una vez validado podrás contactar con artistas VIP.")
            return HttpResponseRedirect('/catalog/' + category_url + '/' + artist_profile_url)
        else:
            return payment_contact(request, artist_profile)
    else:
        return show_contact_information(request, artist_profile)

@login_required
def show_contact_information(request, artist_profile):
    artist_profile.contact_sum += 1
    artist_profile.save()

    return render(request, 'transaction/contact_information.html', {'artist_profile': artist_profile,})

@login_required
def payment_contact(request, artist_profile):
    artist_profile.contact_sum += 1
    artist_profile.save()

    # Create transaction for tracking
    trans = TransactionContact()
    trans.proprietary_member = request.user
    trans.gross_amount = settings.CONTACT_PRICE
    trans.price = trans.gross_amount / (1 + settings.VAT_SPAIN)
    trans.vat = trans.gross_amount - trans.price
    trans.save()

    transitem = TransactionContactItem()
    transitem.transaction = trans
    transitem.artist_user_id = artist_profile.proprietary_user.id
    transitem.artist_profile = artist_profile
    transitem.item_id = "AC-" + str(artist_profile.id)
    transitem.description = "Contactar con " + unidecode(artist_profile.artistic_name)
    transitem.unit_gross_amount = settings.CONTACT_PRICE
    transitem.quantity = 1
    transitem.save()

    return render(request, 'transaction/contact_payment.html', {
        'artist_profile': artist_profile, 'transitem': transitem, 'trans': trans}
    )

@login_required
def payment_subscription(request, plan):
    if request.user.artist_plan == plan:
        return HttpResponseRedirect('/upgradeplan/')

    if plan == '3':
        template = 'upgrade_plan_starter.html'
        item_id = 'SU-PLA1'
        description = "Suscripcion plan Iniciado 1 mes"
        gross_amount = settings.SUBSCRIPTION_STARTER
    elif plan == '2':
        template = 'upgrade_plan_unlimited.html'
        item_id = 'SU-DIA1'
        description = "Suscripcion plan Ilimitado 1 mes"
        gross_amount = settings.SUBSCRIPTION_UNLIMITED

    # Create trasaction for tracking
    trans = TransactionSubscription()
    trans.proprietary_member = request.user
    trans.gross_amount = gross_amount
    trans.price = trans.gross_amount / (1+ settings.VAT_SPAIN)
    trans.vat = trans.gross_amount - trans.price
    trans.save()

    transitem = TransactionSubscriptionItem()
    transitem.transaction = trans
    transitem.item_id = item_id
    transitem.description = description
    transitem.unit_gross_amount = gross_amount
    transitem.quantity = 1
    transitem.save()

    return render(request, template, {'trans':trans, 'transitem': transitem})

@require_GET
def paypal_pdt(request, item_check_callable=None, context=None):
    """
        Override paypal.standard.pdt.views.pdt
        Payment data transfer implementation: http://tinyurl.com/c9jjmw
    """
    context = context or {}
    pdt_obj = None
    txn_id = request.GET.get('tx')
    failed = False
    if txn_id is not None:
        # If an existing transaction with the id tx exists: use it
        try:
            pdt_obj = PayPalPDT.objects.get(txn_id=txn_id)
        except PayPalPDT.DoesNotExist:
            # This is a new transaction so we continue processing PDT request
            pass

        if pdt_obj is None:
            form = PayPalPDTForm(request.GET)
            if form.is_valid():
                try:
                    pdt_obj = form.save(commit=False)
                except Exception, e:
                    error = repr(e)
                    failed = True
            else:
                error = form.errors
                failed = True

            if failed:
                pdt_obj = PayPalPDT()
                pdt_obj.set_flag("Invalid form. %s" % error)

            pdt_obj.initialize(request)

            if not failed:
                # The PDT object gets saved during verify
                pdt_obj.verify(item_check_callable)
    else:
        failed = True
        pass # we ignore any PDT requests that don't have a transaction id

    if not failed:
        if pdt_obj.item_number[:2] == 'AC':
            return paypal_pdt_contact(request, pdt_obj)
        elif pdt_obj.item_number[:2] == 'SU':
            return paypal_pdt_susbcription(request, pdt_obj)
        else:
            template = "transaction/pdt_error.html"
    else:
        template = "transaction/pdt_error.html"

    context.update({"pdt_obj":pdt_obj,})

    return render_to_response(template, context, RequestContext(request))

def paypal_pdt_contact(request, pdt_obj):
    trans = TransactionContact.objects.get(id=int(pdt_obj.invoice))
    transitem = TransactionContactItem.objects.get(transaction=trans)

    context = {'pdt_obj':pdt_obj, 'trans':trans,}

    if not validate_payment(trans, transitem, pdt_obj):
        template = "transaction/pdt_error.html"
    else:
        trans.payment_complete = True
        trans.paypal_ref = pdt_obj.txn_id

        if request.user.promoter_validated or request.user.agency_validated:
            artist_id = int(pdt_obj.item_number[3:])
            artist_profile = ArtistProfile.objects.get(id=artist_id)
            trans.contact_provided = True
            template = "transaction/pdt_contact_validated.html"
            context.update({'artist_profile':artist_profile})
        else:
            template = "transaction/pdt_contact_no_validated.html"
        trans.save()

    return render_to_response(template, context, RequestContext(request))

def paypal_pdt_susbcription(request, pdt_obj):
    trans = TransactionSubscription.objects.get(id=int(pdt_obj.invoice))
    transitem = TransactionSubscriptionItem.objects.get(transaction=trans)

    context = {"pdt_obj":pdt_obj,}

    if not validate_payment(trans, transitem, pdt_obj):
        template = "transaction/pdt_error.html"
    else:
        template = "upgrade_plan_completed.html"

    return render_to_response(template, context, RequestContext(request))
