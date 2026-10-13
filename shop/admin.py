from django.contrib import admin
from django.db.models import Count

from .models import Album_image, Album_image_gallery


class GalleryInline(admin.TabularInline):
    model = Album_image_gallery
    extra = 1


@admin.register(Album_image)
class Album_image_admin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'price', 'like_total', 'views']
    list_filter = ['title', 'price', 'is_active', 'year']
    search_fields = ['title', 'price', 'is_active', 'year']
    list_editable = ['price', 'is_active']
    list_display_links = ['title']
    ordering = ['title']
    inlines = [GalleryInline]
    # shown, but nobody can edit the counter by hand
    readonly_fields = ['views']
    # likes are made by users, not typed in the admin
    exclude = ['slug', 'likes']

    def get_queryset(self, request):
        # count the likes in ONE query for the whole list
        return super().get_queryset(request).annotate(_likes=Count('likes'))

    @admin.display(description='Likes', ordering='_likes')
    def like_total(self, obj):
        return obj._likes
