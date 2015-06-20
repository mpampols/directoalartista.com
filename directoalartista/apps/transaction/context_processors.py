from django.conf import settings

def paypal_variables(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {
        'PAYPAL_RECEIVER_EMAIL': settings.PAYPAL_RECEIVER_EMAIL,
        'PAYPAL_NOTIFY_URL': settings.PAYPAL_NOTIFY_URL,
        'PAYPAL_RETURN_URL': settings.PAYPAL_RETURN_URL,
        'PAYPAL_CANCEL_RETURN': settings.PAYPAL_CANCEL_RETURN,
        'PAYPAL_API_URL': settings.PAYPAL_API_URL,
        'PAYPAL_URL': settings.PAYPAL_URL
    }
