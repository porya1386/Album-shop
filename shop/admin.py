from django.contrib import admin
from .models import Album_image, Album_image_gallery
# Register your models here.


class GalleryInline(admin.TabularInline):
    model = Album_image_gallery
    extra = 1


@admin.register(Album_image)
class Album_image_admin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'price']
    list_filter = ['title', 'price', 'is_active', 'year']
    search_fields = ['title', 'price', 'is_active', 'year']
    list_editable = ['price', 'is_active']
    list_display_links = ['title']
    ordering = ['title']
    inlines = [GalleryInline]
    exclude = ['slug']
