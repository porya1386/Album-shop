from django.db import models
from django.utils.text import slugify


# Album Image Data
class Album_image(models.Model):
    title = models.CharField(max_length=160,null=True,verbose_name='Album Image Title',help_text='Enter Youre Album Image Title',blank=False)
    price = models.PositiveBigIntegerField(default=0,help_text='Enter Youre Album Image Price',verbose_name='Album Image Price',blank=False)
    description = models.TextField(blank=True,help_text='Enter Youre description for youre Album Image',verbose_name='Album Image Description') 
    image = models.ImageField(verbose_name='Album Image',help_text='Upload youre Image ',upload_to='shop/album_image')
    slug = models.SlugField(blank=False,null=True)
    size = models.CharField(blank=False,null=True,help_text='Enter Youre Album Image Size like 60 x 90 cm',verbose_name='Album Image Size')
    year = models.DateField(null=True,verbose_name='Album Image Time Creation',help_text='Enter The Time u Created masterpiece')
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True,verbose_name='Sold or not',help_text='Validate if u have the album or did u sell it already')


    def __str__(self):
        return f"{self.title} {self.is_active} {self.price}"
    # Saving slug fields before it write to data
    def save(self,*args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

