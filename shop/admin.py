from django.contrib import admin
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from .models import Album_image, Album_image_gallery, Sculpture, Sculpture_gallery


class GalleryInline(admin.TabularInline):
    model = Album_image_gallery
    extra = 1


@admin.register(Album_image)
class Album_image_admin(admin.ModelAdmin):
    list_display = ['title', 'title_fa', 'is_active',
                    'price', 'price_toman', 'like_total', 'views']
    list_filter = ['title', 'price', 'is_active', 'year']
    search_fields = ['title', 'title_fa', 'price', 'is_active', 'year']
    list_editable = ['price', 'price_toman', 'is_active']
    list_display_links = ['title']
    ordering = ['title']
    inlines = [GalleryInline]
    # shown, but nobody can edit the counter by hand
    readonly_fields = ['views']
    # likes are made by users, not typed in the admin
    exclude = ['slug', 'likes']

    def get_queryset(self, request):
        # count the likes in ONE query for the whole list
        return super().get_queryset(request).annotate(_likes=Count('likes', distinct=True))

    @admin.display(description=_('Likes'), ordering='_likes')
    def like_total(self, obj):
        return obj._likes


class SculptureGalleryInline(admin.TabularInline):
    model = Sculpture_gallery
    extra = 1


@admin.register(Sculpture)
class Sculpture_admin(admin.ModelAdmin):
    list_display = ['title', 'title_fa', 'material',
                    'is_active', 'price', 'price_toman', 'like_total', 'views']
    list_filter = ['material', 'is_active', 'year']
    search_fields = ['title', 'title_fa', 'size']
    list_editable = ['price', 'price_toman', 'is_active']
    list_display_links = ['title']
    ordering = ['title']
    inlines = [SculptureGalleryInline]
    readonly_fields = ['views']
    # likes are made by users, not typed in the admin
    exclude = ['slug', 'likes']

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_likes=Count('likes', distinct=True))

    @admin.display(description=_('Likes'), ordering='_likes')
    def like_total(self, obj):
        return obj._likes
