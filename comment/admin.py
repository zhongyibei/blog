from django.contrib import admin
from .models import Comment
# Register your models here.

class CommentAdmin(admin.ModelAdmin):
    list_display = ['id','parent','content_object','text','comment_time','user']

admin.site.register(Comment,CommentAdmin)