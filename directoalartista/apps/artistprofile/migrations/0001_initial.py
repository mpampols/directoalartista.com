# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields
import djorm_pgfulltext.fields
import directoalartista.apps.artistprofile.models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtistCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='nombre')),
                ('slug', models.SlugField(verbose_name='slug')),
                ('active', models.BooleanField(default=True, verbose_name='activo')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('order', models.IntegerField(default=0)),
                ('description', models.TextField(null=True, blank=True)),
                ('meta_keywords', models.CharField(default=b'', help_text=b'Keywords for the search engine', max_length=100, blank=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='parent', blank=True, to='artistprofile.ArtistCategory', null=True)),
            ],
            options={
                'ordering': ('tree_id', 'lft'),
                'abstract': False,
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ArtistEventTypeCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='nombre')),
                ('slug', models.SlugField(verbose_name='slug')),
                ('active', models.BooleanField(default=True, verbose_name='activo')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('order', models.IntegerField(default=0)),
                ('description', models.TextField(null=True, blank=True)),
                ('meta_keywords', models.CharField(default=b'', help_text=b'Keywords for the search engine', max_length=100, blank=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='parent', blank=True, to='artistprofile.ArtistEventTypeCategory', null=True)),
            ],
            options={
                'ordering': ('tree_id', 'lft'),
                'abstract': False,
                'verbose_name_plural': 'Event type categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ArtistPicture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_main', models.BooleanField(default=False, help_text=b'Designates whether the artistic profile image is main')),
                ('image', models.ImageField(max_length=255, upload_to=directoalartista.apps.artistprofile.models.content_file_name)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ArtistProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('artistic_name', models.CharField(max_length=100)),
                ('artistic_name_normalized', models.CharField(max_length=100)),
                ('slug', models.SlugField(default=b'', unique=True, max_length=255)),
                ('min_price', models.IntegerField(max_length=10)),
                ('max_price', models.IntegerField(max_length=10)),
                ('show_description', models.TextField()),
                ('show_description_normalized', models.TextField(default=b'')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_published', models.BooleanField(default=True, help_text=b'Designates whether the artistic profile is published')),
                ('is_vip', models.BooleanField(default=False, help_text=b'Designates whether the artistic profile is VIP')),
                ('contact_sum', models.IntegerField(default=0, help_text=b'Sum of the contact button clicks')),
                ('search_index', djorm_pgfulltext.fields.VectorField(default=b'', serialize=False, null=True, editable=False, db_index=True)),
                ('category', models.ForeignKey(related_name='category', to='artistprofile.ArtistCategory')),
                ('event_type', models.ManyToManyField(related_name='event_type', to='artistprofile.ArtistEventTypeCategory')),
                ('proprietary_user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['proprietary_user__artist_plan', '-date_modified', '-date_created'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ArtistProfileUrlHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(default=b'', unique=True, max_length=255)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('artistprofile', models.ForeignKey(to='artistprofile.ArtistProfile')),
            ],
            options={
                'get_latest_by': 'date_created',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ArtistProvince',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='nombre')),
                ('slug', models.SlugField(verbose_name='slug')),
                ('active', models.BooleanField(default=True, verbose_name='activo')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('order', models.IntegerField(default=0)),
                ('description', models.TextField(null=True, blank=True)),
                ('meta_keywords', models.CharField(default=b'', help_text=b'Keywords for the search engine', max_length=100, blank=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='parent', blank=True, to='artistprofile.ArtistProvince', null=True)),
            ],
            options={
                'ordering': ('tree_id', 'lft'),
                'abstract': False,
                'verbose_name_plural': 'provinces',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ArtistVideo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('video_url', models.URLField(default=b'', max_length=100, validators=[directoalartista.apps.artistprofile.models.validate_video_url])),
                ('video_id', models.CharField(default=b'', max_length=30)),
                ('video_service', models.CharField(default=b'', max_length=10)),
                ('artistprofile', models.ForeignKey(related_name='videos', to='artistprofile.ArtistProfile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='artistprovince',
            unique_together=set([('parent', 'name')]),
        ),
        migrations.AddField(
            model_name='artistprofile',
            name='provinces',
            field=models.ManyToManyField(related_name='provinces', to='artistprofile.ArtistProvince'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artistprofile',
            name='secondary_categories',
            field=models.ManyToManyField(related_name='secondary_categories', to='artistprofile.ArtistCategory', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='artistpicture',
            name='artistprofile',
            field=models.ForeignKey(related_name='images', to='artistprofile.ArtistProfile'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='artisteventtypecategory',
            unique_together=set([('parent', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='artistcategory',
            unique_together=set([('parent', 'name')]),
        ),
    ]
