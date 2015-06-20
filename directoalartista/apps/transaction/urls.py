from django.conf.urls import *

from directoalartista.apps.transaction import views as TransactionViews


urlpatterns = patterns('',
    # payment
    url(r'^paypal/pdt/', 'directoalartista.apps.transaction.views.paypal_pdt'),
    url(r'^paypal/ipn-xxx/', include('paypal.standard.ipn.urls'))
)