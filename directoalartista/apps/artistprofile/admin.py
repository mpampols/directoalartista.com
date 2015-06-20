# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin

from django.contrib.contenttypes import generic

from categories.admin import CategoryBaseAdminForm, CategoryBaseAdmin

from directoalartista.apps.artistprofile.models import ArtistProfile, ArtistCategory, \
    ArtistEventTypeCategory, ArtistPicture, ArtistVideo

from categories.models import Category


class ArtistPictureInline(admin.TabularInline):
    model = ArtistVideo

class ArtistVideoInline(admin.TabularInline):
    model = ArtistPicture

class ArtistProfileAdminForm(admin.ModelAdmin):
    inlines = [
        ArtistPictureInline,
        ArtistVideoInline
    ]

    list_display = ('proprietary_user', 'id', 'artistic_name', 'date_created', 'date_modified', 'is_vip', 'contact_sum',
                    'is_published')

    list_filter = ('proprietary_user__user_type', 'proprietary_user__artist_plan', 'is_vip', 'is_published')

    ordering = ('-date_created',)
    search_fields = ('proprietary_user__email', 'artistic_name', 'id')

    class Meta:
        model = ArtistProfile

class ArtistEventTypeAdminForm(CategoryBaseAdminForm):
    class Meta:
        model = ArtistEventTypeCategory
        exclude = []

class ArtistEventTypeCategoryAdmin(CategoryBaseAdmin):
    form = ArtistEventTypeAdminForm
    list_display = ('name', 'active')
    fieldsets = (
        (None, {
            'fields': ('parent', 'name', 'active')
        }),
        ('Meta Data', {
            'fields': ('description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
    )

class ArtistCategoryAdminForm(CategoryBaseAdminForm):
    class Meta:
        model = ArtistCategory
        exclude = []

class ArtistCategoryAdmin(CategoryBaseAdmin):
    form = ArtistCategoryAdminForm
    list_display = ('name', 'active')
    fieldsets = (
        (None, {
            'fields': ('parent', 'name', 'active')
        }),
        ('Meta Data', {
            'fields': ('description', 'meta_keywords'),
            'classes': ('collapse',),
        }),
    )


admin.site.register(ArtistProfile, ArtistProfileAdminForm)
admin.site.register(ArtistCategory)
admin.site.register(ArtistEventTypeCategory)

# Unregister the standard category fields registered by categories.category
admin.site.unregister(Category)