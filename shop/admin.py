from django.contrib import admin
from .models import Album_image, Album_image_gallery
# Register your models here.


class GalleryInline(admin.TabularInline):
    model = Album_image_gallery
    extra = 1


@admin.register(Album_image)
class Album_image_admin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'price']
    inlines = [GalleryInline]
    exclude = ['slug']
