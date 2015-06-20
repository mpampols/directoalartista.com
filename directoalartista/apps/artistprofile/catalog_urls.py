from django.conf.urls import *

from directoalartista.apps.transaction import views as TransactionViews
from directoalartista.apps.artistprofile import views as ArtistProfileViews


# /catalog
urlpatterns = patterns('',
    url(r'^$', ArtistProfileViews.catalog_view, name='catalog'),
    url(r'^(?P<category_url>[-\w]+)/$', ArtistProfileViews.catalog_view_category,
        name='catalog_view_category'
    ),
    url(r'^(?P<category_url>[-\w]+)/(?P<artist_profile_url>[-\w]+)/$', ArtistProfileViews.artist_profile_view,
        name='artistprofile_view'
    ),
    url(r'^(?P<category_url>[-\w]+)/(?P<artist_profile_url>[-\w]+)/contact/$', TransactionViews.contact_artist,
        name='contact_artist'
    )
)