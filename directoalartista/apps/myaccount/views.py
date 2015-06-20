from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext, loader
from django.contrib.auth import logout
from django.contrib import messages
from django.views.decorators.cache import never_cache

from directoalartista.apps.myaccount.forms import GenericUserEditProfileFormArtist, GenericUserEditProfileFormAgency, \
    GenericUserEditProfileFormPromoter
from directoalartista.apps.genericuser.models import GenericUser
from directoalartista.apps.artistprofile.models import ArtistProfile
from directoalartista.apps.plancontrol.models import ArtistPlan


@login_required
@never_cache
def profile(request):
    artist_plans = {
        "4": "Gratuito",
        "3": "Iniciado",
        "2": "Ilimitado"
    }

    if request.user.user_type == 'A':
        # A = Artists
        artist_profiles = ArtistProfile.objects.filter(proprietary_user_id=request.user.id)
        user_plan = ArtistPlan.objects.filter(user=request.user)
        context = {'artist_profiles': artist_profiles}

        if user_plan:
            plan = user_plan.order_by('id').reverse()[0]
            if plan.expiration_date:
                expiration_date = str(plan.expiration_date.day) + "/" + str(plan.expiration_date.month) + "/" +\
                                  str(plan.expiration_date.year)
                context.update({'plan_expiration_date': expiration_date})

        return render(request, 'myaccountartist.html', context)

    elif request.user.user_type == 'P':
        # P = Promoters
        return render(request, 'myaccountpromoter.html')
    elif request.user.user_type == 'G':
        # G = Agencies
        artist_profiles = ArtistProfile.objects.filter(proprietary_user_id=request.user.id)
        context = {'artist_profiles': artist_profiles}

        return render(request, 'myaccountagency.html', {
            'artist_profiles': artist_profiles,
            'user_plan':artist_plans[request.user.artist_plan],
        })
    else:
        return HttpResponseRedirect('/admin')

@login_required
def edit_profile(request):
    if request.user.user_type == 'A':
        # A = Artists
        form_class = GenericUserEditProfileFormArtist
        template_name = 'myaccount_edit_profile_artist.html'

        if request.method == 'POST':
            user_form = GenericUserEditProfileFormArtist(request.POST, instance=request.user)

            if user_form.is_valid():
                user_form.save()
                request.user.setUserNewsletterSubscription('artist', request.user.artist_plan)
                messages.success(request, "Se han guardado los cambios")
                return HttpResponseRedirect('/accounts/profile')
        else:
            user_form = GenericUserEditProfileFormArtist(instance=request.user)

        return render_to_response(template_name, {'user_form': user_form,}, context_instance=RequestContext(request))

    if request.user.user_type == 'P':
        # P = Promoters
        form_class = GenericUserEditProfileFormPromoter
        template_name = 'myaccount_edit_profile_promoter.html'

        if request.method == 'POST':
            user_form = GenericUserEditProfileFormPromoter(request.POST, instance=request.user)

            if user_form.is_valid():
                user_form.save()
                request.user.setUserNewsletterSubscription('promoter', '')
                messages.success(request, "Se han guardado los cambios")
                return HttpResponseRedirect('/accounts/profile')
        else:
            user_form = GenericUserEditProfileFormPromoter(instance=request.user)

        return render_to_response(template_name, {'user_form': user_form,}, context_instance=RequestContext(request))

    if request.user.user_type == 'G':
        # G = Agencies
        form_class = GenericUserEditProfileFormAgency
        template_name = 'myaccount_edit_profile_agency.html'

        if request.method == 'POST':
            user_form = GenericUserEditProfileFormAgency(request.POST, instance=request.user)

            if user_form.is_valid():
                user_form.save()
                request.user.setUserNewsletterSubscription('agency', '')
                messages.success(request, "Se han guardado los cambios")
                return HttpResponseRedirect('/accounts/profile')
        else:
            user_form = GenericUserEditProfileFormAgency(instance=request.user)

        return render_to_response(template_name, {'user_form': user_form,}, context_instance=RequestContext(request))

@login_required
def disable_user(request):
    request.user.is_active = False
    artist_profiles = ArtistProfile.objects.filter(id=request.user.id)
    for i in artist_profiles:
        i.delete()
    if request.user.user_type == 'A':
        # A = Artists
        request.user.artist_plan = '4' # free
    request.user.save()
    request.user.setUserNewsletterSubscription('unregistered', '')
    logout(request)
    return render(request, 'account_disabled.html')