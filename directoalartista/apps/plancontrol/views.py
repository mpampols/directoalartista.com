# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from premailer import transform
from django.core.mail import EmailMultiAlternatives

from directoalartista.apps.transaction.views import payment_subscription
from directoalartista.apps.plancontrol.backend import free_change_plan


@login_required
def contract_plan(request, plan):
    if request.user.user_type != 'A':
        return HttpResponseRedirect('/accounts/profile')

    if request.user.artist_plan == plan:
        return HttpResponseRedirect('/upgradeplan/')
    if plan == '4':
        return render(request, 'upgrade_plan_free.html')
    elif plan == '3':
        return payment_subscription(request, plan)
    elif plan == '2':
        return payment_subscription(request, plan)
    else:
        return HttpResponseRedirect('/accounts/profile/')

@login_required
def contract_free(request):
    free_change_plan(request.user, '4')
    if request.user.artist_plan != '4':
        template = 'upgrade_plan_free_in_wait.html'
    else:
        template = 'upgrade_plan_completed.html'
    return render(request, template)