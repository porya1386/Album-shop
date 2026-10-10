from django.contrib import admin
from .models import Album_image
# Register your models here.

@admin.register(Album_image)
class Album_image_admin(admin.ModelAdmin):
    list_display = ['title','is_active','price']
    exclude = ['slug']