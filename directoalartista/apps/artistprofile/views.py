# -*- coding: utf-8 -*-
from django.contrib.sitemaps import ping_google
from django.shortcuts import render_to_response, render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest, Http404
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib import messages
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Avg
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.cache import cache

import hashlib
import operator
import random
import json

from django.views.decorators.cache import cache_page, never_cache
from django.views.decorators.http import require_POST
from django.views.generic.edit import CreateView
from django.http import HttpResponse

from directoalartista.apps.artistprofile import forms
from django.conf import settings
from moneyed import Money, EUR
import unicodedata

from directoalartista.apps.artistprofile.forms import ArtistProfileForm, EditArtistProfileForm, EditArtistPictureForm, SearchCatalogForm, \
    EditArtistVideoForm
from directoalartista.apps.artistprofile.models import ArtistProfile, ArtistCategory, ArtistEventTypeCategory, \
    ArtistPicture, ArtistVideo, ArtistProvince, ArtistProfileUrlHistory
from directoalartista.apps.genericuser.models import GenericUser

from django.contrib.auth import get_user_model
User = get_user_model()


# in seconds (1 hour) used in catalog_view
SEED_CACHE_TIME = 3600

# maximum number of different results, used in catalog_view
NUM_RANDOM_RESULTS = 30

# maximum number of filter lists that appear below search selectors
HOME_SEARCH_FILTER_LIST_LIMIT = 4

# price ranges for catalog search form
PRICE_RANGES = {
                   1: (0, 0),
                   2: (1, 100),
                   3: (101, 200),
                   4: (201, 400),
                   5: (401, 800),
                   6: (801, 1500),
                   7: (1501, 4000),
                   8: (3001, 6000),
                   9: (6001, 15000),
                   10: (15000, 999999)
}


@login_required
@never_cache
def artist_profile_add(request):
    if request.user.user_type == 'A' and ArtistProfile.objects.filter(proprietary_user=request.user).count() > 0:
        raise Http404
    elif request.user.user_type == 'P':
        raise Http404
    elif request.user.user_type == 'G' and not request.user.agency_validated:
        raise Http404

    template_name = 'artistprofile/add.html'

    if request.method == 'POST':
        artist_profile_form = ArtistProfileForm(request.POST, request.FILES)

        if artist_profile_form.is_valid():
            new = ArtistProfile()
            new.proprietary_user = request.user
            new.artistic_name = artist_profile_form.cleaned_data['artistic_name']
            new.artistic_name_normalized = unicodedata.normalize(
                "NFKD",
                artist_profile_form.cleaned_data['artistic_name']
            ).encode('ASCII', 'ignore')

            artist_profile_name_slug = slugify(unicode(artist_profile_form.cleaned_data['artistic_name']))
            new_slug = artist_profile_name_slug + "-" + hashlib.md5(artist_profile_name_slug + str(request.user.id)).hexdigest()[:5]
            new.slug = new_slug

            new.category = ArtistCategory.objects.get(id=artist_profile_form.data['category'])
            new.min_price = artist_profile_form.cleaned_data['min_price']
            new.max_price = artist_profile_form.cleaned_data['max_price']
            new.show_description = artist_profile_form.cleaned_data['show_description']
            new.show_description_normalized = unicodedata.normalize(
                "NFKD",
                artist_profile_form.cleaned_data['show_description']
            ).encode('ASCII', 'ignore')
            if ('is_vip' in artist_profile_form.data):
                new.is_vip = True
            new.is_published = True
            new.save()

            # Extra security checks
            # If a user tries to save more fields than permitted, we'll ignore them
            owner_plan = new.get_owner_plan()
            max_eventtypes = settings.USER_LIMITS["artistprofile_max_eventtypes_" + owner_plan]
            max_secondarycategories = settings.USER_LIMITS["artistprofile_max_secondarycategories_" + owner_plan]
            max_provinces = settings.USER_LIMITS["artistprofile_max_provinces_" + owner_plan]

            for event_type_id in artist_profile_form.cleaned_data['event_type']:
                if (new.event_type.count() < max_eventtypes):
                    new.event_type.add(event_type_id)

            for secondary_category_id in artist_profile_form.cleaned_data['secondary_categories']:
                if (new.secondary_categories.count() < max_secondarycategories):
                    new.secondary_categories.add(secondary_category_id)

            for province_id in artist_profile_form.cleaned_data['provinces']:
                if (new.provinces.count() < max_provinces):
                    new.provinces.add(province_id)

            for filename, file in request.FILES.iteritems():
                if 'image' in filename:
                    image = ArtistPicture(artistprofile_id=new.id, image=file)
                    image.save()
                    image.create_resizes()
                    image.save()

            for video, video_url in artist_profile_form.data.iteritems():
                if 'video' in video:
                    video = ArtistVideo(artistprofile_id=new.id, video_url=video_url)
                    video.save()

            # Add this new slug to the user's history
            new_artistprofileurlhistory = ArtistProfileUrlHistory()
            new_artistprofileurlhistory.artistprofile = ArtistProfile.objects.get(id=new.id)
            new_artistprofileurlhistory.slug = new_slug
            new_artistprofileurlhistory.save()

            # Ping google and tell there's a new artist profile
            update_sitemap()

            messages.success(request, "La ficha de artista se ha creado correctamente. Es momento de subir "
                                      "tus mejores fotos y vídeos")
            return HttpResponseRedirect('/artistprofile/edit/media/' + str(new.id))
    else:
        artist_profile_form = ArtistProfileForm()

    return render_to_response(template_name, {'artist_profile_form': artist_profile_form,},
                              context_instance=RequestContext(request)
    )

@login_required
@never_cache
def artist_profile_addvideo(request, artist_profile_id):
    response_data = {}
    artist_profile = ArtistProfile.objects.get(id=artist_profile_id)
    max_videos_per_plan = settings.USER_LIMITS['artistprofile_max_videos_' + artist_profile.get_owner_plan()]

    if request.user != artist_profile.proprietary_user:
        raise Http404

    if (artist_profile.get_video_quantity() == max_videos_per_plan):
        response_data['status'] = "warning"
        response_data['result'] = "Has llegado al límite de vídeos para el plan contratado."
    else:
        if request.is_ajax():
            form = EditArtistVideoForm(request.POST)
            video_url = request.POST['videoupload']
            video = ArtistVideo(artistprofile_id=artist_profile.id, video_url=video_url)

            try:
                video.save()
                # data serialization
                response_data['status'] = "success"
                response_data['result'] = "Vídeo publicado correctamente."
                response_data['video_url'] = str(video.get_thumbnail_url())
                response_data['video_id'] = str(video.id)
            except:
                # data serialization
                response_data['status'] = "error"
                response_data['result'] = "La URL del vídeo no es correcta."
                response_data['video_url'] = str(video.get_thumbnail_url())
                response_data['video_id'] = str(video.id)

            #response_data['artist_profile_slug'] = artist_profile_url
            response_data['artist_profile_id'] = artist_profile_id
            response_data['static_url'] = settings.STATIC_URL

            return HttpResponse(json.dumps(response_data), content_type="text/plain")

        response_data['status'] = "warning"
        response_data['result'] = "Lo sentimos, algo ha salido mal. Asegúrate que la URL del vídeo tiene el formato correcto."

    return HttpResponse(json.dumps(response_data), content_type='text/plain')

@login_required
@never_cache
def artist_profile_upload(request, artist_profile_id):
    response_data = {}
    try:
        artist_profile = ArtistProfile.objects.get(id=artist_profile_id)
    except ArtistProfile.DoesNotExist:
        raise Http404

    artist_profile_id = artist_profile.id
    max_pictures_per_plan = settings.USER_LIMITS['artistprofile_max_pictures_' + artist_profile.get_owner_plan()]

    if request.user != artist_profile.proprietary_user:
        raise Http404

    if (artist_profile.get_picture_quantity() == max_pictures_per_plan):
        response_data['status'] = "warning"
        response_data['result'] = "Has llegado al límite de fotos para el plan contratado."
    else:
        if request.is_ajax() or request.method == 'POST':
            form = EditArtistPictureForm(request.POST, request.FILES)
            uploaded_file = request.FILES['upload']

            image = ArtistPicture(artistprofile_id=artist_profile.id, image=uploaded_file)
            image.save()

            if not image.create_resizes():
                image.delete()
                response_data['status'] = "warning"
                response_data['result'] = "Lo sentimos, algo ha salido mal. Asegúrate que la foto tiene el formato correcto."
                return HttpResponse(json.dumps(response_data), content_type='text/plain')

            # set this picture as highlighted if it's the only one uploaded
            if (artist_profile.get_picture_quantity() == 1):
                image.set_main_picture()
                response_data['is_main'] = True
            else:
                response_data['is_main'] = False

            image.save()

            # data serialization
            response_data['status'] = "success"
            response_data['result'] = "Foto publicada correctamente."
            response_data['picture_url'] = str(image.get_image_name_template_03())
            response_data['picture_id'] = str(image.id)
            response_data['artist_profile_id'] = str(artist_profile_id)
            response_data['static_url'] = settings.STATIC_URL
            response_data['media_url'] = settings.MEDIA_URL

            return HttpResponse(json.dumps(response_data), content_type="text/plain")

        response_data['status'] = "warning"
        response_data['result'] = "Lo sentimos, algo ha salido mal. Asegúrate que la foto tiene el formato correcto."

    return HttpResponse(json.dumps(response_data), content_type='text/plain')

@login_required
@never_cache
def artist_profile_edit(request, artist_profile_id):
    template_name = 'artistprofile/edit.html'
    try:
        artist_profile = ArtistProfile.objects.get(id=artist_profile_id)
    except ArtistProfile.DoesNotExist:
        raise Http404
    artist_profile_url = artist_profile.slug

    if request.user != artist_profile.proprietary_user:
        raise Http404

    if request.method == 'POST':
        artist_profile_form = EditArtistProfileForm(request.POST, request.FILES, instance=artist_profile)

        if artist_profile_form.is_valid():

            # Extra security checks
            # If a user tries to save more fields than permitted, we'll ignore them
            owner_plan = artist_profile.get_owner_plan()
            max_eventtypes = settings.USER_LIMITS["artistprofile_max_eventtypes_" + owner_plan]
            max_secondarycategories = settings.USER_LIMITS["artistprofile_max_secondarycategories_" + owner_plan]
            max_provinces = settings.USER_LIMITS["artistprofile_max_provinces_" + owner_plan]

            artist_profile_name_slug = slugify(unicode(artist_profile_form.cleaned_data['artistic_name']))
            artist_profile_slug = artist_profile_name_slug + "-" + hashlib.md5(artist_profile_name_slug + str(request.user.id)).hexdigest()[:5]

            slug_changed = False
            if (artist_profile_slug != artist_profile.slug):
                artist_profile.slug = artist_profile_slug
                artist_history = ArtistProfileUrlHistory.objects.filter(slug=artist_profile_slug)
                if artist_history.count() == 0:
                    slug_changed = True

            artist_profile.artistic_name_normalized = unicodedata.normalize(
                "NFKD",
                artist_profile_form.cleaned_data['artistic_name']
            ).encode('ASCII', 'ignore')

            if ('is_vip' in artist_profile_form.data):
                artist_profile.is_vip = True
            else:
                artist_profile.is_vip = False

            artist_profile.event_type.clear()
            for event_type_id in artist_profile_form.cleaned_data['event_type']:
                if (artist_profile.event_type.count() < max_eventtypes):
                    artist_profile.event_type.add(event_type_id)

            artist_profile.secondary_categories.clear()
            for secondary_category_id in artist_profile_form.cleaned_data['secondary_categories']:
                if (artist_profile.secondary_categories.count() < max_secondarycategories):
                    artist_profile.secondary_categories.add(secondary_category_id)

            artist_profile.provinces.clear()
            for province_id in artist_profile_form.cleaned_data['provinces']:
                if (artist_profile.provinces.count() < max_provinces):
                    artist_profile.provinces.add(province_id)

            for filename, file in request.FILES.iteritems():
                if 'image' in filename:
                    image = ArtistPicture(artistprofile_id=artist_profile.id, image=file)
                    image.save()
                    image.create_resizes()
                    image.save()

            for video, video_url in artist_profile_form.data.iteritems():
                if 'video' in video:
                    video = ArtistVideo(artistprofile_id=artist_profile.id, video_url=video_url)
                    video.save()

            artist_profile.min_price = artist_profile_form.cleaned_data['min_price']
            artist_profile.max_price = artist_profile_form.cleaned_data['max_price']
            artist_profile.show_description = artist_profile_form.cleaned_data['show_description']
            artist_profile.show_description_normalized = unicodedata.normalize(
                "NFKD",
                artist_profile_form.cleaned_data['show_description']
            ).encode('ASCII', 'ignore')

            artist_profile.date_modified = timezone.now()
            artist_profile.save()

            if slug_changed:
                # Add this new slug to the user's history
                new_artistprofileurlhistory = ArtistProfileUrlHistory()
                new_artistprofileurlhistory.artistprofile = ArtistProfile.objects.get(id=artist_profile.id)
                new_artistprofileurlhistory.slug = artist_profile_slug
                new_artistprofileurlhistory.save()

            # Ping google and tell there's a new artist profile
            update_sitemap()

            messages.success(request, "Se han guardado los cambios")
            return HttpResponseRedirect('/accounts/profile')
    else:
        artist_profile_form = EditArtistProfileForm(instance=artist_profile)
        artist_profile_images = ArtistPicture.objects.filter(artistprofile=artist_profile.id).order_by('id')
        artist_profile_videos = ArtistVideo.objects.filter(artistprofile=artist_profile.id).order_by('id')

        return render_to_response(template_name, {'artist_profile_form': artist_profile_form,
                                                  'artist_profile_images': artist_profile_images,
                                                  'artist_profile_videos': artist_profile_videos,
                                                  'artist_profile_slug': artist_profile_url,
                                                  'artist_profile_id': artist_profile_id},
                                  context_instance=RequestContext(request)
        )

    messages.error(request, "Ha ocurrido un error y los cambios no se han guardado correctamente, "
                            "por favor, vuelve a intentarlo.")
    return render_to_response(template_name, {'artist_profile_form': artist_profile_form,},
                              context_instance=RequestContext(request)
    )

@login_required
@never_cache
def artist_profile_edit_media(request, artist_profile_id):
    template_name = 'artistprofile/edit_media.html'
    try:
        artist_profile = ArtistProfile.objects.get(id=artist_profile_id)
    except ArtistProfile.DoesNotExist:
        raise Http404

    if request.user != artist_profile.proprietary_user:
        raise Http404

    artist_profile_form = EditArtistProfileForm(instance=artist_profile)
    artist_profile_images = ArtistPicture.objects.filter(artistprofile=artist_profile.id).order_by('id')
    artist_profile_videos = ArtistVideo.objects.filter(artistprofile=artist_profile.id)

    return render_to_response(template_name, {'artist_profile_form': artist_profile_form,
                                              'artist_profile_images': artist_profile_images,
                                              'artist_profile_videos': artist_profile_videos,
                                              'artist_profile_id': artist_profile_id},
                              context_instance=RequestContext(request)
    )

@login_required
@never_cache
def artist_profile_publish(request, artist_profile_id):
    try:
        artist_profile = ArtistProfile.objects.get(id=artist_profile_id)
    except ArtistProfile.DoesNotExist:
        raise Http404

    if request.user != artist_profile.proprietary_user:
        raise Http404

    if artist_profile.is_published:
        artist_profile.is_published = False
    else:
        artist_profile.is_published = True
    artist_profile.save()
    messages.success(request, "Se han guardado los cambios")
    return HttpResponseRedirect('/accounts/profile')

@login_required
@never_cache
def delete_artist_picture(request, artist_profile_picture_id, artist_profile_id):
    try:
        artist_profile = ArtistProfile.objects.get(id=artist_profile_id)
    except ArtistProfile.DoesNotExist:
        raise Http404
    picture = ArtistPicture.objects.filter(id=artist_profile_picture_id).get()
    is_main = picture.is_main

    if (picture.artistprofile.proprietary_user != request.user):
        raise Http404

    picture.delete()

    # check if the deleted picture was the main one, if so, mark as main the latest one
    if (is_main):
        actual_pictures = ArtistPicture.objects.filter(artistprofile_id=artist_profile.id)
        if actual_pictures:
            actual_pictures[0].set_main_picture()

    messages.success(request, "Foto eliminada correctamente")
    return HttpResponseRedirect('/artistprofile/edit/' + artist_profile_id)

@login_required
@never_cache
def delete_artist_video(request, artist_profile_video_id, artist_profile_id):
    video = ArtistVideo.objects.filter(id=artist_profile_video_id).get()
    video.delete()

    messages.success(request, "Vídeo eliminado correctamente")
    return HttpResponseRedirect('/artistprofile/edit/' + artist_profile_id)

@login_required
@never_cache
def highlight_artist_picture(request, artist_profile_picture_id, artist_profile_id):
    ArtistPicture.objects.filter(id=artist_profile_picture_id).get().set_main_picture()
    messages.success(request, "Seleccionada como nueva foto principal")
    return HttpResponseRedirect('/artistprofile/edit/' + artist_profile_id)

@login_required
@never_cache
def artist_profile_delete(request, artist_profile_id):
    try:
        artist_profile = ArtistProfile.objects.get(id=artist_profile_id)
    except ArtistProfile.DoesNotExist:
        raise Http404
    if request.user != artist_profile.proprietary_user:
        raise Http404

    artist_profile.delete()
    messages.success(request, "Se ha eliminado la ficha de artista")
    return HttpResponseRedirect('/accounts/profile')

def artist_profile_view(request, category_url, artist_profile_url):
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
                settings.BASE_URL + '/catalog/' + str(found_artist_category.slug) + '/' + found_artist_profile.slug
            )
        except ArtistProfileUrlHistory.DoesNotExist:
            raise Http404

    if artist_profile.is_published == True or request.user.id == artist_profile.proprietary_user_id:
        images = ArtistPicture.objects.filter(artistprofile_id=artist_profile.id, is_main=False)
        videos = ArtistVideo.objects.filter(artistprofile_id=artist_profile.id).order_by('id')
        try:
            main_image = ArtistPicture.objects.get(artistprofile_id=artist_profile.id, is_main=True)
        except:
            main_image = ''
        return render(request, 'artistprofile/view.html', {
            'artist_profile': artist_profile,
            'videos': videos,
            'images': images,
            'main_image': main_image
        })
    else:
        return HttpResponseRedirect('/catalog')

def catalog_view_category(request, category_url):
    try:
        category = ArtistCategory.objects.get(slug=category_url)
    except ArtistCategory.DoesNotExist:
        raise Http404
    # TODO: Check why we need distinct
    artist_list = ArtistProfile.objects.filter(Q(category__id__exact=category.id)|
                                               Q(secondary_categories__id__exact=category.id) |
                                               Q(category__parent__exact=category.id) |
                                               Q(secondary_categories__parent__exact=category.id))\
                                 .distinct()

    artist_profiles = catalog_paginator(request, artist_list)
    search_form = SearchCatalogForm()

    return render(request, 'catalog.html', {
        'artist_profiles': artist_profiles, 'search_form': search_form, 'category': category.name,
        },
        context_instance=RequestContext(request)
    )

def catalog_view(request):
    full_search = True

    query = request.GET.get('q')
    if query:
        query = unicodedata.normalize("NFKD", query).encode('ASCII', 'ignore')
        artist_list = ArtistProfile.objects.search(query)
        full_search = False
    else:
        artist_list = ArtistProfile.objects.all()

    # Ensure that only published artists are listed
    artist_list = artist_list.filter(is_published=True)

    # Search engine
    search_province = request.GET.get('province')
    if search_province and search_province != '0':
        artist_list = artist_list.filter(Q(provinces__id__exact=search_province))
        full_search = False

    search_category = request.GET.get('category')
    if search_category and search_category != '0':
        artist_list = artist_list.filter(Q(category__id__exact=search_category) |
                                         Q(secondary_categories__id__exact=search_category) |
                                         Q(category__parent__exact=search_category) |
                                         Q(secondary_categories__parent__exact=search_category))\
                                 .distinct()
        full_search = False

    search_event_type = request.GET.get('event_type')
    if search_event_type and search_event_type != '0':
        artist_list = artist_list.filter(Q(event_type__id__exact=search_event_type))
        full_search = False

    search_price = request.GET.get('price')
    if search_price and search_price != '0':
        if int(search_price) >= 1 and int(search_price) <= 10:
            min_price = PRICE_RANGES[int(search_price)][0]
            max_price = PRICE_RANGES[int(search_price)][1]
        else:
            min_price = 0
            max_price = 9999999
        artist_list = artist_list.filter(max_price__gte=min_price, min_price__lte=max_price)
        full_search = False

    if full_search:
        # We will try to randomize results and save the objects as a list inside the cache
        # Got the idea from: http://stackoverflow.com/questions/4022535/how-to-have-a-random-order-on-a-set-of-objects-with-paging-in-django

        # Check if session exists
        if not request.session.get('catalog_view_full_cache'):
            random_seed = random.randint(1, NUM_RANDOM_RESULTS)
            request.session['catalog_view_full_cache'] = random_seed

        # Get the actual session seed
        artist_list = cache.get('catalog_view_full_cache_' + str(request.session['catalog_view_full_cache']))

        # If session seed doesn't exists, run the query and save it to a list
        if not artist_list:
            artist_list = list(
                 ArtistProfile.objects.all().filter(is_published=True)\
                                            .order_by('proprietary_user__artist_plan', '?')
            )

            # Save the result to memory
            cache.set('catalog_view_full_cache_' + str(request.session['catalog_view_full_cache']),
                      artist_list,
                      SEED_CACHE_TIME)

    # Paginator + search
    queries_without_page = request.GET.copy()
    if queries_without_page.has_key('page'):
        del queries_without_page['page']

    artist_profiles = catalog_paginator(request, artist_list)

    search_form = SearchCatalogForm(request.GET or None)

    return render(request, 'catalog.html', {
        'artist_profiles': artist_profiles, 'search_form': search_form, 'queries': queries_without_page,
        }
    )

def catalog_paginator(request, artist_list):
    paginator = Paginator(artist_list, 12)

    page = request.GET.get('page')
    try:
        artist_profiles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        artist_profiles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        artist_profiles = paginator.page(paginator.num_pages)

    return artist_profiles

@cache_page(60 * 60 * 24)
def home_view(request):
    search_form = SearchCatalogForm()
    return render(request, 'home.html', {
        'search_form': search_form,
        'most_provinces_list': most_provinces_list,
        'most_categories_list': most_categories_list,
        'most_eventtypes_list': most_eventtypes_list,
        'most_prices_list': most_prices_list,
        })

def update_sitemap():
    try:
        ping_google()
    except IOError:
        # TODO: Create an error logging app to save or send this exceptions as alerts
        pass

def most_provinces_list():
    """
    :return: list of HOME_SEARCH_FILTER_LIST_LIMIT provinces with more artistprofiles
    """
    artistprofiles_per_province = []
    for province in ArtistProvince.objects.annotate():
        num_profiles = ArtistProfile.objects.filter(provinces=province).count()
        artistprofiles_per_province.append({
            'id': province.id,
            'name': province.name,
            'num_profiles': num_profiles,
        })

    return sorted(artistprofiles_per_province,
                  lambda x, y: cmp(x['num_profiles'], y['num_profiles']),
                  reverse=True)[:HOME_SEARCH_FILTER_LIST_LIMIT]

def most_categories_list():
    """
    :return: list of HOME_SEARCH_FILTER_LIST_LIMIT categories with more artistprofiles
    """
    artistprofiles_per_category = []
    for category in ArtistCategory.objects.annotate():
        num_profiles = ArtistProfile.objects.filter(Q(category=category) |
                                                    Q(category__parent=category) |
                                                    Q(secondary_categories=category) |
                                                    Q(secondary_categories__parent=category))\
            .distinct()\
            .count()

        artistprofiles_per_category.append({
            'id': category.id,
            'name': category.name,
            'num_profiles': num_profiles
        })

    return sorted(artistprofiles_per_category,
                  lambda x, y: cmp(x['num_profiles'], y['num_profiles']),
                  reverse=True)[:HOME_SEARCH_FILTER_LIST_LIMIT]

def most_eventtypes_list():
    """
    :return: list of HOME_SEARCH_FILTER_LIST_LIMIT eventtypes with more artistprofiles
    """
    artistprofiles_per_eventtype = []
    for eventtype in ArtistEventTypeCategory.objects.annotate():
        num_profiles = ArtistProfile.objects.filter(event_type=eventtype).count()
        artistprofiles_per_eventtype.append({
            'id': eventtype.id,
            'name': eventtype.name,
            'num_profiles': num_profiles
        })

    return sorted(artistprofiles_per_eventtype,
                  lambda x, y: cmp(x['num_profiles'], y['num_profiles']),
                  reverse=True)[:HOME_SEARCH_FILTER_LIST_LIMIT]

def most_prices_list():
    """
    Search for the average min price / max price and show the nearby prices from this ones
    :return: list of HOME_SEARCH_FILTER_LIST_LIMIT prices with more artistprofiles
    """
    avg_min_price = ArtistProfile.objects.all().aggregate(Avg('min_price'))
    avg_max_price = ArtistProfile.objects.all().aggregate(Avg('max_price'))
    artistprofiles_per_range = []
    selected_ranges = []
    price_ranges = {}

    for p in PRICE_RANGES:

        if int(avg_min_price['min_price__avg']) >= PRICE_RANGES[p][0] \
                and int(avg_min_price['min_price__avg']) <= PRICE_RANGES[p][1]:

            if (p > 1):
                price_ranges[0] = "De %s a %s €" % (str(PRICE_RANGES[p-1][0]), str(PRICE_RANGES[p-1][1]))

                profiles_per_range = ArtistProfile.objects.filter(
                    min_price__lte=PRICE_RANGES[p-1][1],
                    max_price__gte=PRICE_RANGES[p-1][0],
                ).count()

                if (profiles_per_range > 0):
                    artistprofiles_per_range.append({
                        'id': p-1,
                        'name': "De %s a %s €" % (str(PRICE_RANGES[p-1][0]), str(PRICE_RANGES[p-1][1])),
                        'num_profiles': profiles_per_range
                    })
                    selected_ranges.append(p-1)

            profiles_per_range = ArtistProfile.objects.filter(
                min_price__lte=PRICE_RANGES[p][1],
                max_price__gte=PRICE_RANGES[p][0],
            ).count()

            if (profiles_per_range > 0 and p not in selected_ranges):
                artistprofiles_per_range.append({
                    'id': p,
                    'name': "De %s a %s €" % (str(PRICE_RANGES[p][0]), str(PRICE_RANGES[p][1])),
                    'num_profiles': profiles_per_range
                })
                selected_ranges.append(p)

        if int(avg_max_price['max_price__avg']) >= PRICE_RANGES[p][0] \
                and int(avg_max_price['max_price__avg']) <= PRICE_RANGES[p][1]:

            profiles_per_range = ArtistProfile.objects.filter(
                min_price__lte=PRICE_RANGES[p][1],
                max_price__gte=PRICE_RANGES[p][0],
            ).count()

            if (profiles_per_range > 0 and p not in selected_ranges):
                artistprofiles_per_range.append({
                    'id': p,
                    'name': "De %s a %s €" % (str(PRICE_RANGES[p][0]), str(PRICE_RANGES[p][1])),
                    'num_profiles': profiles_per_range
                })
                selected_ranges.append(p)

            if (p < len(PRICE_RANGES)-1 and p+1 not in selected_ranges):
                price_ranges[0] = "De %s a %s €" % (str(PRICE_RANGES[p+1][0]), str(PRICE_RANGES[p+1][1]))

                profiles_per_range = ArtistProfile.objects.filter(
                    min_price__lte=PRICE_RANGES[p+1][1],
                    max_price__gte=PRICE_RANGES[p+1][0],
                ).count()

                if (profiles_per_range > 0):
                    artistprofiles_per_range.append({
                        'id': p+1,
                        'name': "De %s a %s €" % (str(PRICE_RANGES[p+1][0]), str(PRICE_RANGES[p+1][1])),
                        'num_profiles': profiles_per_range
                    })
                    selected_ranges.append(p+1)

    return artistprofiles_per_range
