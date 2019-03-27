from django.urls import path
from .import views2 as views
urlpatterns = [
    #首页设置
    path('',views.blog_list,name="blog_list"),
    path('music/',views.music,name="music"),
    path('<int:blog_pk>',views.blog_detail,name="blog_detail"),
    path('type/<int:blog_type_pk>',views.blogs_with_type,name="blogs_with_type"),
    path('date/<int:year>/<int:month>',views.blogs_with_date,name="blogs_with_date"),
]