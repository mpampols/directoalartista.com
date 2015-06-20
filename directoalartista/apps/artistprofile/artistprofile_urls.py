from django.conf.urls import *

from directoalartista.apps.transaction import views as TransactionViews
from directoalartista.apps.artistprofile import views as ArtistProfileViews


# /artistprofile
urlpatterns = patterns(
    '',

    # Add
    url(r'^add', ArtistProfileViews.artist_profile_add, name='artistprofile_add'),

    # Edit
    url(r'^edit/(?P<artist_profile_id>[-\w]+)/upload/$', ArtistProfileViews.artist_profile_upload,
        name='artistprofile_upload'
    ),
    url(r'^edit/media/(?P<artist_profile_id>[-\w]+)/upload/$',
        ArtistProfileViews.artist_profile_upload,
        name='artistprofile_upload'
    ),
    url(r'^edit/(?P<artist_profile_id>[-\w]+)/addvideo/$',
        ArtistProfileViews.artist_profile_addvideo,
        name='artistprofile_addvideo'
    ),
    url(r'^edit/media/(?P<artist_profile_id>[-\w]+)/addvideo/$',
        ArtistProfileViews.artist_profile_addvideo,
        name='artistprofile_addvideo'
    ),
    url(r'^edit/(?P<artist_profile_id>[-\w]+)/$', ArtistProfileViews.artist_profile_edit,
        name='artistprofile_edit'
    ),
    url(r'^edit/media/(?P<artist_profile_id>[-\w]+)/$', ArtistProfileViews.artist_profile_edit_media,
        name='artistprofile_edit_media'
    ),

    # Profile actions
    url(r'^(?P<artist_profile_id>[-\w]+)/picture/(?P<artist_profile_picture_id>[-\w]+)/highlight/$',
        ArtistProfileViews.highlight_artist_picture,
        name='artistprofile_highlight'
    ),
    url(r'^(?P<artist_profile_id>[-\w]+)/picture/(?P<artist_profile_picture_id>[-\w]+)/delete/$',
        ArtistProfileViews.delete_artist_picture,
        name='artistprofile_delete'
    ),
    url(r'^(?P<artist_profile_id>[-\w]+)/video/(?P<artist_profile_video_id>[-\w]+)/delete/$',
        ArtistProfileViews.delete_artist_video,
        name='artistprofile_delete'
    ),
    url(r'^publish/(?P<artist_profile_id>[-\w]+)/$', ArtistProfileViews.artist_profile_publish,
        name='artistprofile_publish'
    ),
    url(r'^delete/(?P<artist_profile_id>[-\w]+)/$', ArtistProfileViews.artist_profile_delete,
        name='artistprofile_delete'
    )
)
