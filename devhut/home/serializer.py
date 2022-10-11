from dataclasses import field
from datetime import datetime
from time import time
from rest_framework import serializers


from . models import Blog, BlogCategory, Comments, Follower
from register.serializer import UserSerializer
from register.models import Account

class CommentSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField(source='get_created_at')
    user = UserSerializer()
    class Meta:
        model = Comments
        fields = ['id','user','comment','created_at']
    def get_created_at(self,obj):
        time=timesince(obj.created_at)
        time=time.split(',')[0]
        return time
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['category','category_slug']

class BlogSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    comments = CommentSerializer(many=True)
    category = CategorySerializer()
    created_at = serializers.SerializerMethodField(source='get_created_at')

    class Meta:
        model = Blog
        fields = ['id','author_id','title','content','image',
        'created_at','author','category','read_time','likes','comments']
    def get_created_at(self,obj):
        time=timesince(obj.created_at)
        time=time.split(',')[0]
        return time


class FollowersSerializer(serializers.ModelSerializer):
    user_from=UserSerializer()
    class Meta:
        model = Follower
        fields = ['user_to','user_from']

class AuthorProfileSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    category = CategorySerializer()
    created_at = serializers.SerializerMethodField(source='get_created_at')
    class Meta:
        model = Blog
        fields = ['id','author_id','title','content','image',
        'category','created_at','read_time','likes','author']
    def get_created_at(self,obj):
        time=timesince(obj.created_at)
        time=time.split(',')[0]
        return time


class AuthorDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['first_name','last_name','email','image','about']

class CompilerSerializer(serializers.Serializer):
    output=serializers.CharField()
from django.utils.timesince import timesince
class BlogOnlySerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField(source='get_author')
    category = serializers.SerializerMethodField(source='get_category')
    created_at = serializers.SerializerMethodField(source='get_created_at')
    class Meta:
        model=Blog
        fields=['id','author','is_blocked','category','content','title','read_time','likes','created_at']
    def get_author(self,obj):
        return obj.author.email
    def get_category(self,obj):
        return obj.category.category
    def get_created_at(self,obj):
        created_at=obj.created_at
        return created_at.date()
# for admin page
class AdminPanelCommentSerializer(serializers.ModelSerializer):
    created_at=serializers.SerializerMethodField(source='get_created_at')
    user=serializers.SerializerMethodField(source='get_user')
    class Meta:
        model = Comments
        fields = ['id','user','comment','created_at','is_blocked']
    def get_created_at(self,obj):
        created_at=obj.created_at
        return created_at.date()
    def get_user(self,obj):
        return obj.user.email

          