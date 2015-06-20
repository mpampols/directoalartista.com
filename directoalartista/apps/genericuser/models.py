# -*- coding: utf-8 -*-
import mailchimp
from django.db import models
from django.conf import settings

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.utils.http import urlquote
from django.core.mail import EmailMultiAlternatives

from django.template import Template
from django.template.loader import get_template
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from premailer import transform

from localflavor.es.es_provinces import PROVINCE_CHOICES

from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

#from django.contrib.auth import get_user_model
#User = get_user_model()


class GenericUserManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=GenericUserManager.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email,
            password=password
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class GenericUser(AbstractBaseUser, PermissionsMixin):

    class Meta:
        swappable = 'AUTH_USER_MODEL'

    email = models.EmailField(max_length=254, unique=True, db_index=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=False)
    last_name = models.CharField(_('last name'), max_length=60, blank=False)

    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                   'site.'))

    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                    'active. Unselect this instead of deleting accounts.'))

    # Defines the user type
    USER_TYPES = (
        ('A', 'Artist'),
        ('G', 'Agency'),
        ('P', 'Promoter'),
    )
    user_type = models.CharField(max_length=2, blank=False, choices=USER_TYPES,
                                    help_text=_('Designates user type, A: Artist, G: Agency, P: Promoter'))

    # Fields for a generic user
    phone = models.CharField(max_length=20, blank=False)
    dni = models.CharField(max_length=10, blank=True)
    address = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=80, blank=True)
    province = models.CharField(max_length=50, blank=True, choices=PROVINCE_CHOICES)
    newsletter_subscription = models.BooleanField(default=True)

    # Fields for Artist user
    ARTIST_PLANS = (
        ("4", "Free"),
        ("3", "Starter"),
        ("2", "Unlimited")
    )

    artist_plan = models.CharField(max_length=15, blank=True, null=True, choices=ARTIST_PLANS)
    slug = models.SlugField(max_length=255, blank=False, default='')

    # Fields for Agency user
    agency_name = models.CharField(max_length=255, blank=True, null=True)
    agency_company_name = models.CharField(max_length=255, blank=True, null=True)
    agency_cif = models.CharField(max_length=10, blank=True)
    agency_additional_info = models.TextField(blank=True, null=True)
    agency_validated = models.BooleanField(default=False)

    # Fields for Promoter user
    promoter_room_or_event_name = models.CharField(max_length=255, blank=True, null=True)
    promoter_company_name = models.CharField(max_length=255, blank=True, null=True)
    promoter_cif = models.CharField(max_length=10, blank=True)
    promoter_additional_info = models.TextField(blank=True, null=True)
    promoter_validated = models.BooleanField(default=False)

    objects = GenericUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def email_user(self, subject, message, from_email=None):
        """
        Sends an email to this User.
        """
        subject, from_email = 'Activa tu cuenta', 'Directo al Artista <noreply@directoalartista.com>'
        html_content = render_to_string('email/global/template.html', {
            'email_title': 'Activa tu cuenta',
            'email_content': message,
        })

        html_content = transform(html_content)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, from_email, [self.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)

        return True

    def setUserNewsletterSubscription(self, user_type, user_plan):
        """
        Activates or deactivates the newsletter subscription inside mailchimp
        """
        m = mailchimp.Mailchimp(settings.MAILCHIMP_API)
        list_id = settings.MAILCHIMP_LIST_ID
        if self.newsletter_subscription:
            #listid, email, options, email type, send email to confirm subscription
            #update existing user, replace interests, send welcome
            m.lists.subscribe(
                list_id,
                {'email': self.email},
                {
                    'fname': self.first_name,
                    'LNAME': self.last_name,
                    'ut': user_type,
                    'plan': user_plan
                },
                'html',
                'false',
                'true',
                'true',
                'true'
            )
        else:
            try:
                m.lists.unsubscribe(list_id,
                        {'email': self.email},
                        False,
                        False,
                        False)
            except:
                pass
        return True

    def save(self, *args, **kwargs):
        super(GenericUser, self).save(*args, **kwargs)

