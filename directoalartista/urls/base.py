from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap

from django.views.generic import TemplateView
from directoalartista.apps.artistprofile.models import ArtistProfile
from directoalartista.apps.artistprofile import views as ArtistProfileViews

admin.autodiscover()

# SITEMAPS Variable
# This is the queryset that defines the objects to show in the sitemap file
# We're now rendering a list of artist profiles ordered by modification date
artists_dict = {
    'queryset': ArtistProfile.objects.all(),
    'date_field': 'date_modified'
}

# SITEMAPS Variable
# This dictionary sets the content types that we want to render in the sitemap XML file
# By now, only flat pages and artists
sitemaps = {
    'flatpages': FlatPageSitemap,
    'artists': GenericSitemap(artists_dict, priority=0.8)
}

urlpatterns = patterns(
    '',

    # static pages
    url(r'^$', ArtistProfileViews.home_view, name='home'),
    url(r'^faq', TemplateView.as_view(template_name='faq.html'), name='faq'),
    url(r'^legal', TemplateView.as_view(template_name='legal.html'), name='legal'),
    url(r'^cookies', TemplateView.as_view(template_name='cookies.html'), name='cookies'),
    url(r'^about', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^register', TemplateView.as_view(template_name='register.html'), name='register'),
    url(r'^how', TemplateView.as_view(template_name='how.html'), name='how'),

    # sitemaps
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),

    # robots.txt
    url(r'^robots\.txt$', TemplateView.as_view(template_name='system/robots.txt', content_type='text/plain')),

    # humans.txt
    url(r'^humans\.txt$', TemplateView.as_view(template_name='system/humans.txt', content_type='text/plain')),

    # humans.txt
    url(r'^browserconfig\.xml$', TemplateView.as_view(template_name='system/browserconfig.xml', content_type='text/xml')),

    # directoalartista.apps.artistprofile
    url(r'^artistprofile/', include('directoalartista.apps.artistprofile.artistprofile_urls')),
    url(r'^catalog/', include('directoalartista.apps.artistprofile.catalog_urls')),

    # directoalartista.apps.contact
    url(r'^contact/', include('directoalartista.apps.contact.urls')),

    # directoalartista.apps.genericuser accounts
    url(r'^accounts/', include('directoalartista.apps.genericuser.accounts_urls')),

    # directoalartista.apps.genericuser registration and account
    url(r'^', include('directoalartista.apps.genericuser.urls')),

    # directoalartista.apps.transaction
    url(r'^', include('directoalartista.apps.transaction.urls')),

    # directoalartista.apps.plancontrol upgradeplan
    url(r'^upgradeplan/', include('directoalartista.apps.plancontrol.upgradeplan_urls')),

    # admin
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls))
)
