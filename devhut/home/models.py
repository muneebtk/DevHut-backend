from email.policy import default
from django.utils import timezone
from django.db import models
from register.models import Account

class BlogCategory(models.Model):
    category = models.CharField(max_length=100)
    category_slug = models.SlugField(max_length=100,unique=True)

    def __str__(self):
        return self.category

class Blog(models.Model):
    author = models.ForeignKey(Account,on_delete=models.CASCADE)
    category = models.ForeignKey(BlogCategory,on_delete=models.CASCADE)
    title = models.TextField()
    image = models.ImageField(upload_to='images')
    content = models.TextField()
    read_time = models.CharField(max_length=10,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    likes = models.IntegerField(default=0)
    is_liked = models.BooleanField(default=False)
    is_blocked=models.BooleanField(default=False)

    def __str__(self):
        return self.title

class Comments(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog,related_name='comments',on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    is_blocked=models.BooleanField(default=False)

    def __str__(self):
        return self.comment

class Follower(models.Model):
    user_from = models.ForeignKey(Account,related_name='rel_from_set',on_delete=models.CASCADE)
    user_to = models.ForeignKey(Account,related_name='rel_to_set',on_delete=models.CASCADE)

class Likes(models.Model):
    from_user = models.ForeignKey(Account,related_name='from_like',on_delete=models.CASCADE)
    to_blog = models.ForeignKey(Blog,related_name='to_blog',on_delete=models.CASCADE)
    liked_at=models.DateTimeField(default=timezone.now)

 