from django.contrib import admin
from .models import BlogType,Blog
# Register your models here.

class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ['type_name']

class BlogAdmin(admin.ModelAdmin):
    list_display = ['title','blog_type','author','get_read_num','created_time','last_updated_time']



admin.site.register(BlogType,BlogTypeAdmin)
admin.site.register(Blog,BlogAdmin)
