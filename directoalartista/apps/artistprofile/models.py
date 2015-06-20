# -*- coding: utf-8 -*-
from django.db import models
from django.views.decorators.cache import never_cache
import moneyed
import urlparse
import hashlib
import shutil
import urllib2
import json
import os

from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from djmoney.models.fields import MoneyField
from django.utils.translation import ugettext_lazy as _

from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.db.models.signals import post_delete
from django.dispatch import receiver

from djorm_pgfulltext.models import SearchManager
from djorm_pgfulltext.fields import VectorField

from directoalartista.apps.genericuser.models import GenericUser
from django.conf import settings

import categories
from categories.models import CategoryBase


def validate_artistic_name(value):
    slug = slugify(unicode(value))
    slug_count = ArtistProfile.objects.filter(slug=slug)
    if slug_count.count():
        raise ValidationError('Artist profile exist!')

def validate_video_url(value):
    query = urlparse.urlparse(value)
    if query.hostname in ('youtu.be', 'www.youtube.com', 'youtube.com', 'www.vimeo.com', 'vimeo.com'):
        pass
    else:
        raise ValidationError('Video URL incorrect!')

def content_file_name(self, filename):
    filename = filename.encode('ascii', 'replace')
    url = "files/artistprofiles/%s" % (filename)
    return url

class ArtistEventTypeCategory(CategoryBase):
    order = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    meta_keywords = models.CharField(
        blank=True,
        default="",
        max_length=100,
        help_text="Keywords for the search engine"
    )

    def save(self, *args, **kwargs):
        super(ArtistEventTypeCategory, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta(CategoryBase.Meta):
        verbose_name_plural = 'Event type categories'

    class MPTTMeta:
        order_insertion_by = ('order', 'name')


class ArtistCategory(CategoryBase):
    order = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    meta_keywords = models.CharField(
        blank=True,
        default="",
        max_length=100,
        help_text="Keywords for the search engine"
    )

    def save(self, *args, **kwargs):
        super(ArtistCategory, self).save(*args, **kwargs)

    class Meta(CategoryBase.Meta):
        verbose_name_plural = 'categories'

    class MPTTMeta:
        order_insertion_by = ('order', 'name')


class ArtistProvince(CategoryBase):
    order = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    meta_keywords = models.CharField(
        blank=True,
        default="",
        max_length=100,
        help_text="Keywords for the search engine"
    )

    def save(self, *args, **kwargs):
        super(ArtistProvince, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta(CategoryBase.Meta):
        verbose_name_plural = 'provinces'

    class MPTTMeta:
        order_insertion_by = ('order', 'name')


class ArtistProfile(models.Model):
    proprietary_user = models.ForeignKey(GenericUser)
    """Proprietary of this artist profile, as it can be an artist or a agency"""

    artistic_name = models.CharField(max_length=100)
    artistic_name_normalized = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, blank=False, default='', unique=True)
    category = models.ForeignKey(ArtistCategory, related_name="category")
    secondary_categories = models.ManyToManyField(ArtistCategory, blank=True, related_name="secondary_categories")
    event_type = models.ManyToManyField(ArtistEventTypeCategory, related_name="event_type")
    provinces = models.ManyToManyField(ArtistProvince, related_name="provinces")
    min_price = models.IntegerField(max_length=10)
    max_price = models.IntegerField(max_length=10)
    show_description = models.TextField(blank=False, null=False)
    show_description_normalized = models.TextField(blank=False, null=False, default="")
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True, help_text=('Designates whether the artistic profile is published'))
    is_vip = models.BooleanField(default=False, help_text=('Designates whether the artistic profile is VIP'))
    contact_sum = models.IntegerField(default=0, help_text=('Sum of the contact button clicks'))

    search_index = VectorField()

    objects = SearchManager(
        fields = ('artistic_name_normalized', 'show_description_normalized'),
        config = 'pg_catalog.english', # this is default
        search_field = 'search_index', # this is default
        auto_update_search_field = True
    )

    class Meta:
        ordering = ['proprietary_user__artist_plan', '-date_modified', '-date_created']

    def __unicode__(self):
        return self.artistic_name

    def get_published_status(self):
        return self.is_published

    def get_owner_plan(self):
        return self.proprietary_user.artist_plan

    def get_owner_plan_name(self):
        artist_plans = {
            "4": "Gratuito",
            "3": "Iniciado",
            "2": "Ilimitado"
        }
        return artist_plans[self.proprietary_user.artist_plan]

    def get_secondary_categories(self):
        objects = self.secondary_categories.all()
        list = []
        for i in objects:
            url = ', <a href="/catalog/' + i.slug + '">' + i.name + '</a>'
            list.append(url)
        return ''.join(list)

    def get_secondary_categories_flat(self):
        objects = self.secondary_categories.all()
        list = []
        for i in objects:
            name = ', ' + i.name + ''
            list.append(name)
        return ''.join(list)

    def get_provinces(self):
        objects = self.provinces.all()
        if objects.count() == 52:
            return 'Todas las provincias'
        list = []
        for i in objects:
            list.append(i.name)
        return ', '.join(list)

    def get_event_type(self):
        objects = self.event_type.all()
        list = []
        for i in objects:
            list.append(i.name)
        return ', '.join(list)

    def get_picture_quantity(self):
        return len(ArtistPicture.objects.filter(artistprofile_id=self.id))

    def get_video_quantity(self):
        return len(ArtistVideo.objects.filter(artistprofile_id=self.id))

    def get_image_catalog_03(self):
        image = ArtistPicture.objects.filter(artistprofile_id=self.id).get(is_main=True)
        if image:
            return image.get_image_name_template_03()
        else:
            return False

    def get_image_catalog_04(self):
        image = ArtistPicture.objects.filter(artistprofile_id=self.id).get(is_main=True)
        if image:
            return image.get_image_name_template_04()
        else:
            return False

    def get_image_catalog_05(self):
        image = ArtistPicture.objects.filter(artistprofile_id=self.id).get(is_main=True)
        if image:
            return image.get_image_name_template_05()
        else:
            return False

    def get_absolute_url(self):
        return "/catalog/" + str(self.category.slug) + "/" + str(self.slug)

    def get_price(self):
        if self.min_price == self.max_price:
            price = "{:,}".format(self.max_price) + ' €'
            return price.replace(',', '.')
        else:
            price = 'entre ' + "{:,}".format(self.min_price) + ' € y ' + "{:,}".format(self.max_price) + ' €'
            return price.replace(',', '.')


class ArtistProfileUrlHistory(models.Model):
    artistprofile = models.ForeignKey(ArtistProfile)
    slug = models.SlugField(max_length=255, blank=False, default='', unique=True)
    date_created = models.DateTimeField(default=timezone.now)

    class Meta:
        get_latest_by = "date_created"


class ArtistPicture(models.Model):
    """
    Image sizes
    '00': original
    '01': very small 50px
    '02': artistic profile small 110px
    '03': catalog 150px
    '04': my account 200px
    '05': artistic profile big 340px
    '06': big 600px
    """
    artistprofile = models.ForeignKey(ArtistProfile, related_name="images")
    is_main = models.BooleanField(default=False, help_text=("Designates whether the artistic profile image is main"))
    image = models.ImageField(upload_to=content_file_name, max_length=255)

    # Set our max thumbnail size in a tuple (max width, max height)
    image_sizes = {
        '01': (120, 120),
        '02': (220, 220),
        '03': (410, 410),
        '04': (780, 780),
        '05': (960, 960),
        '06': (1200, 1200),
    }

    def set_main_picture(self):
        images = ArtistPicture.objects.filter(artistprofile_id=self.artistprofile.id)

        # Set all other artist profile pictures to False
        for image in images:
            image.is_main = False
            image.save()

        # Set actual picture to be the main one
        self.is_main = True
        self.save()

    def get_image_name(self, artistprofile_id, image_id, size_id):
        list = [str(artistprofile_id), str(image_id), str(size_id)]
        string = '-'.join(list)
        return hashlib.md5(string).hexdigest()

    def create_resizes(self):
        from PIL import Image, ImageOps
        from cStringIO import StringIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        import os

        # Open original image using PIL's Image
        try:
            image_orig = Image.open(StringIO(self.image.read()))
        except:
            storage, path = self.image.storage, self.image.path
            storage.delete(path)
            # TODO: Add proper error handling with custom exception
            return False

        # Convert to RGB if necessary
        if image_orig.mode not in ('L', 'RGB'):
            image_orig = image_orig.convert('RGB')

        # Rewrite original image with new name and JPG format
        try:
            image = image_orig.copy()
            temp_handle = StringIO()
            image.save(temp_handle, 'jpeg')
            temp_handle.seek(0)
            image_name = self.get_image_name(self.artistprofile_id, self.id, '00')
            suf = SimpleUploadedFile(image_name, temp_handle.read(), content_type='image/jpeg')
            self.image.close()
        except:
            # TODO: Add proper error handling with custom exception
            return False

        # Delete original uploaded image
        try:
            storage, path = self.image.storage, self.image.path
            storage.delete(path)
            self.image.save('%s.jpg'%(image_name), suf, save=False)
        except:
            # TODO: Add proper error handling with custom exception
            return False

        for size in self.image_sizes:
            image = image_orig.copy()
            temp_handle = StringIO()

            w = self.image_sizes[size][0]
            h = image_orig.size[1] / self.image_sizes[size][1]

            if (size == '05' or size == '06'):
                image.thumbnail(size, Image.ANTIALIAS)
            else:
                if (image_orig.size[0] < image_orig.size[1]):
                    new_width = self.image_sizes[size][0]
                    aspect_ratio = float(image_orig.size[1]) / float(image_orig.size[0])
                    new_height = int(float(self.image_sizes[size][0]) * float(aspect_ratio))
                else:
                    new_height = self.image_sizes[size][1]
                    aspect_ratio = float(image_orig.size[0]) / float(image_orig.size[1])
                    new_width =  int(float(self.image_sizes[size][1]) * float(aspect_ratio))

                image = image.resize((new_width, new_height), Image.ANTIALIAS)

            image.save(temp_handle, 'jpeg')
            temp_handle.seek(0)

            image_name = self.get_image_name(self.artistprofile_id, self.id, size)
            suf = SimpleUploadedFile(image_name, temp_handle.read(), content_type='image/jpeg')
            self.image.save('%s.jpg'%(image_name), suf, save=False)

        return True

    def __unicode__(self):
        return self.image.name

    def save(self, *args, **kwargs):
        super(ArtistPicture, self).save(*args, **kwargs)

    def get_image_name_template_00(self):
        return self.get_image_name(self.artistprofile_id, self.id, '00')

    def get_image_name_template_01(self):
        return self.get_image_name(self.artistprofile_id, self.id, '01')

    def get_image_name_template_02(self):
        return self.get_image_name(self.artistprofile_id, self.id, '02')

    def get_image_name_template_03(self):
        return self.get_image_name(self.artistprofile_id, self.id, '03')

    def get_image_name_template_04(self):
        return self.get_image_name(self.artistprofile_id, self.id, '04')

    def get_image_name_template_05(self):
        return self.get_image_name(self.artistprofile_id, self.id, '05')

    def get_image_name_template_06(self):
        return self.get_image_name(self.artistprofile_id, self.id, '06')


class ArtistVideo(models.Model):
    artistprofile = models.ForeignKey(ArtistProfile, related_name="videos")
    video_url = models.URLField(blank=False, default="", max_length=100, validators=[validate_video_url])
    video_id = models.CharField(blank=False, default="", max_length=30)
    video_service = models.CharField(blank=False, default="", max_length=10)

    def set_service_and_id(self, *args, **kwargs):
        """
        Compatible with YouTube and Vimeo
        Examples:
        - http://youtu.be/SA2iWivDJiE
        - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
        - http://www.youtube.com/embed/SA2iWivDJiE
        - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
        - http://www.vimeo.com/81730491

        Returns True if service and id can be setted, False otherwise
        """

        query = urlparse.urlparse(self.video_url)
        if query.hostname == 'youtu.be':
            self.video_id = query.path[1:]
            self.video_service = 'youtube'
        elif query.hostname in ('www.youtube.com', 'youtube.com'):
            self.video_service = 'youtube'
            if query.path == '/watch':
                p = urlparse.parse_qs(query.query)
                self.video_id = p['v'][0]
            elif query.path[:7] == '/embed/':
                self.video_id = query.path.split('/')[2]
            elif query.path[:3] == '/v/':
                self.video_id = query.path.split('/')[2]
            else:
                raise ValidationError('Video URL incorrect!')
            return True
        elif query.hostname in ('www.vimeo.com', 'vimeo.com'):
            self.video_service = 'vimeo'
            self.video_id = query.path.lstrip('/')
            return True

        return False

    # returns the thumbnail URL of the video
    # TODO @property <- should we use this kind of method as properties? think so
    def get_thumbnail_url(self):
        try:
            if (self.video_service == "youtube"):
                return "https://img.youtube.com/vi/" + self.video_id + "/2.jpg"
            elif (self.video_service == "vimeo"):
                # get the JSON data of the video
                json_url = "https://vimeo.com/api/v2/video/" + self.video_id + ".json"
                request = urllib2.Request(json_url)
                opener = urllib2.build_opener()
                f = opener.open(request)
                json_data = json.loads(f.read())
                thumbnail_url = json_data[0]['thumbnail_large']
                return thumbnail_url
        except:
            return False

    def save(self, *args, **kwargs):
        if not self.set_service_and_id(self.video_url):
            raise ValidationError("URL incorrecta")
        super(ArtistVideo, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.video_url


@receiver(post_delete, sender=ArtistPicture)
def artistpicture_post_delete_handler(sender, **kwargs):
    photo = kwargs['instance']
    path = os.path.join(settings.MEDIA_ROOT, 'files', 'artistprofiles')
    storage = photo.image.storage
    storage.delete(path + '/' +ArtistPicture.get_image_name(photo, photo.artistprofile_id, photo.id, '00') + '.jpg')
    for i in photo.image_sizes:
        storage.delete(path + '/' +ArtistPicture.get_image_name(photo, photo.artistprofile_id, photo.id, i) + '.jpg')
