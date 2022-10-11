from django.contrib import admin
from. models import Blog, BlogCategory,Likes
from . import models



class BlogAdmin(admin.ModelAdmin):
    fields = ['author','title','content','is_blocked','image','category','read_time','likes']

class CommentAdmin(admin.ModelAdmin):
    fields = ['user','comment','blog']
    readonly_fields=('created_at','modified_at')

class FollowersAdmin(admin.ModelAdmin):
    fields = ['user_from','user_to']

class LikesAdmin(admin.ModelAdmin):
    fields = ['from_user','to_blog','liked_at']

class BlogCategoryAdmin(admin.ModelAdmin):
    fields = ['category','category_slug']

admin.site.register(BlogCategory,BlogCategoryAdmin)
admin.site.register(Blog,BlogAdmin)
admin.site.register(models.Comments,CommentAdmin)
admin.site.register(models.Follower,FollowersAdmin)
admin.site.register(Likes,LikesAdmin)
