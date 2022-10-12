import calendar
from datetime import datetime, timedelta
import sys
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from register.serializer import UserSerializer

from . models import Blog, BlogCategory,Follower, Likes
from . serializer import AdminPanelCommentSerializer, AuthorProfileSerializer,BlogOnlySerializer, BlogSerializer, CategorySerializer, CommentSerializer, CompilerSerializer,FollowersSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated,IsAdminUser,IsAuthenticatedOrReadOnly
from . models import Comments
from register.models import Account
from django.utils.text import slugify
from rest_framework.decorators import permission_classes
from . serializer import AuthorDetailsSerializer

from rest_framework import filters
from rest_framework import generics


class WriteBlogs(APIView):
    # list all blogs or create  
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = ([IsAuthenticated])
    def post(self,request,format=None):
        data=request.data
        try:
            if BlogCategory.objects.filter(category_slug=slugify(data['category'])):
                category = get_object_or_404(BlogCategory,category_slug = slugify(data['category']))
                
            else:
                category = BlogCategory.objects.create(
                category = request.data['category'],
                category_slug = slugify(request.data['category'])
            )
            blog = Blog.objects.create(
                author = request.user,
                title = request.data['title'],
                image = request.FILES['image'],
                content = request.data['content'],
                category = category,
                read_time = request.data['read_time'],
            )
            user = get_object_or_404(Account,email = request.user)
            user.is_staff = True
            user.save()
            return Response(data='Blog added successfully, Now you are one of our community.',status=status.HTTP_201_CREATED)
        except:
            return Response(data='Something goes wrong, Please try again.', status=status.HTTP_400_BAD_REQUEST)

# edit or delete blog
@api_view(['PUT','DELETE','GET'])
@permission_classes([IsAuthenticated])
def EditOrDeleteBlog(request,id):
    # save currepted details 
    if request.method=='PUT':
        data=request.data
        try:
            if BlogCategory.objects.filter(category_slug=slugify(data['category'])):
                category = get_object_or_404(BlogCategory,category_slug = slugify(data['category']))
            else:
                category = BlogCategory.objects.create(
                category = request.data['category'],
                category_slug = slugify(request.data['category'])
            )
            blog=get_object_or_404(Blog,id=id)
            blog.author=request.user
            blog.category=category
            blog.title=request.data['title']
            try:
                blog.image=request.FILES['image']
            except:
                pass
            blog.content=request.data['content']
            blog.read_time=request.data['read_time']
            blog.save()
            return Response('Blog edited successfully.',status=status.HTTP_200_OK)
        except:
            return Response('Something went wrong',status=status.HTTP_202_ACCEPTED)
    
    # delete a blog by author
    elif request.method=='DELETE':
        blog=get_object_or_404(Blog,id=id)
        if request.user==blog.author:
            blog.delete()
            return Response('Blog deleted successfully.')
        else:
            return Response(status=status.HTTP_202_ACCEPTED)

    # get the blog data of a spedified blog
    elif request.method=='GET':
        blog=get_object_or_404(Blog,id=id)
        if blog.author==request.user:
            serializer=BlogOnlySerializer(blog,many=False)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_202_ACCEPTED)


# fething all blogs
from . models import BlogCategory
@api_view(['GET'])
def all_blogs(request):
    blog = Blog.objects.all().exclude(is_blocked=True)
    serializer = BlogSerializer(blog,many=True)
    category = BlogCategory.objects.all()
    cat_serializer = CategorySerializer(category,many=True)
    from_date=datetime.now().date()
    to_date=from_date-timedelta(days=7)

    trending_blogs=Blog.objects.filter().order_by('-likes')[:8]
    trending_serializer = BlogSerializer(trending_blogs,many=True)
    list = {
        'serializer':serializer.data,
        'cat_serializer':cat_serializer.data,
        'trending_blogs':trending_serializer.data,
    }
    return Response(list)

# comments crud operations also like functionality and single blog view function

class CommentList(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
# single blog view
    def get(self,request,id):
        blog = get_object_or_404(Blog,id=id)
        user=get_object_or_404(Account,email=blog.author.email)
        serializer = BlogSerializer(blog,many=False)
        data={
            'serializer':serializer.data,
            'id':user.id,
        }
        return Response(data)
# post a comment
    def post(self,request,id):
        try:
            user=request.user
            comment = Comments()
            comment.user=user
            blog = get_object_or_404(Blog,id=id)
            comment.blog = blog
            comment.comment = request.data['comment']
            comment.save()
            return Response('success')
        except:
            return Response('error founded!')
# like function
    def put(self,request,id):
        try:
            user = request.user
            blog = get_object_or_404(Blog,id=id)
            if not Likes.objects.filter(from_user=user,to_blog=blog).exists():
                like = Likes()
                like.from_user = user
                like.to_blog = blog
                like.save()
                blog = get_object_or_404(Blog,id=blog.id)
                like = blog.likes
                blog.likes += 1
                count=blog.likes
                blog.save()
                user.is_liked=True
                user.save()
                return Response({'status':True,'count':count})
            else:
                Likes.objects.filter(from_user=user,to_blog=blog).delete()
                blog = get_object_or_404(Blog,id=blog.id)
                like = blog.likes
                blog.likes -= 1
                count=blog.likes
                blog.save()
                user.is_liked=False
                user.save()
                return Response({'status':False,'count':count})
        except:
            return Response('Error founded!')
# edit or delete comment
@permission_classes([IsAuthenticated])
@api_view(['GET','PUT','DELETE'])
def EditOrDeleteComment(request,id):
    if request.method=='GET':
        comment=get_object_or_404(Comments,id=id)
        serializer = CommentSerializer(comment,many=False)
        return Response(serializer.data)
    # submit edited comment
    if request.method=='PUT':
        comment = get_object_or_404(Comments,id=id)
        try:
            comment.comment=request.data['comment']
            comment.save()
            return Response('Comment edited success')
        except:
            return Response('Something went wrong!')
    if request.method=='DELETE':
        comment = get_object_or_404(Comments,id=id)
        comment.delete()
        message='Comment deleted'
        return Response({'id':id,'message':message})
            

# author profile class view and crud operations follow functions 
class AuthorProfile(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get(self,request,id):
        blog = Blog.objects.filter(author_id=id)
        serializer = AuthorProfileSerializer(blog,many=True)
        author = get_object_or_404(Account,id=id)
        followers = Follower.objects.filter(user_to=author)
        followerSerializer = FollowersSerializer(followers,many=True)
        seri={
            'author':serializer.data,
            'followers':followerSerializer.data,
            'id':id
        }
        return Response(seri)
# follow a blog author
    def post(self,request,id):
        try:
            user_to = get_object_or_404(Account,id=id)
            user_from = request.user
            if user_to == user_from:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                is_follow=Follower.objects.filter(user_to=user_to,user_from=user_from)
                if is_follow:
                    Follower.objects.filter(user_from=user_from,user_to=user_to).delete()
                    user_to.followers -= 1
                    user_to.save()
                    followers = user_to.followers
                    user_to.is_followed = False
                    return Response({'status':False,'followers':followers},status = status.HTTP_200_OK)
                else:
                    f=Follower()
                    f.user_from = user_from
                    f.user_to = user_to
                    f.save()
                    user_to.followers += 1
                    followers = user_to.followers
                    user_to.save()
                    user_to.is_followed = True
                    return Response({'status':True,'followers':followers},status=status.HTTP_200_OK)
        except: 
            return Response('Something goes wrong.',status=status.HTTP_400_BAD_REQUEST)
@api_view(["GET"])
def categoryView(request,slug):
    if slug is not None:
        cat_slug = get_object_or_404(BlogCategory,category_slug=slug)
        blogs = Blog.objects.filter(category=cat_slug)
        serializer=  BlogSerializer(blogs,many=True)
        return Response(serializer.data)
    else:
        return Response('No slug appears')

# edit author profile details 
@api_view(['GET','POST','PUT'])
@permission_classes([IsAdminUser])
def EditAuthorProfile(request,id):
    if request.method == 'GET':
        user = get_object_or_404(Account,id=id)
        if user==request.user:
            serializer = AuthorDetailsSerializer(user)
            id=id
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # save users correpted details
    if request.method == 'PUT':
        user = get_object_or_404(Account,id=id)
        if user==request.user:
            try:
                first_name = request.data['first_name']
                last_name = request.data['last_name']
                email = request.data['email']
            except:
                return Response('First 3 fields are required')
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            try:
                user.image = request.FILES['image']
            except:
                pass
            try:
                user.about = request.data['about']
            except:
                pass
            user.save()
            serializer = AuthorDetailsSerializer(user)
            return Response('Details updated successfully.')
        else:
            return Response('You are not the author,Please check!',status=status.HTTP_202_ACCEPTED)

# search function
class SearchBlogListView(generics.ListAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title','category__category']

# follwing blogs
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def followingBlogs(request):
    following_blogs=''
    user = request.user
    follow = Follower.objects.filter(user_from=user)
    for i in follow:
        following_blogs=Blog.objects.filter(author=i.user_to)
    serializer=BlogSerializer(following_blogs,many=True)
    return Response(serializer.data)

# python compiler
@api_view(['POST'])
def pythonCompiler(request):
    try:
        code_area_data = request.data['code_area']
    except:
        return Response('No data')
    try:
        original_stdout = sys.stdout
        sys.stdout = open('file.txt','w')
        exec(code_area_data)
        sys.stdout.close()
        sys.stdout = original_stdout
        output=open('file.txt','r').read()
        serializer=CompilerSerializer(output)
    except Exception as e:
        sys.stdout = original_stdout
        output=str(e)
    return Response({'output':output})

                              #ADMIN SIDE
# admin side functions

# Admin get details of all users
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def getAllUsers(request):
    users = Account.objects.filter(is_staff=False,is_superadmin=False).order_by('id')
    serializer = UserSerializer(users,many=True)
    return Response(serializer.data)
# block or unblock a user 
class AllUsers(APIView):
    permission_classes=[IsAuthenticated]
    def patch(self,request,id):
        user = get_object_or_404(Account,id=id)
        if user.is_active==True:
            user.is_active=False
            user.save()
            return Response({'is_active':user.is_active})
        else:
            user.is_active=True
            user.save()
            return Response({'is_active':user.is_active})

# Admin fetching all blogs
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def getAllBlogs(request):
    blogs=Blog.objects.filter().order_by('id')
    serializer=BlogOnlySerializer(blogs,many=True)
    return Response(serializer.data)
# block or unblock a user by admin
@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def BlockOrUnBlockBlog(request,id):
    blog=get_object_or_404(Blog,id=id)
    if blog.is_blocked==True:
        blog.is_blocked=False
        blog.save()
        return Response({'is_active':blog.is_blocked})
    else:
        blog.is_blocked=True
        blog.save()
        return Response({'is_active':blog.is_blocked})
# fetching all writers
@api_view(['GET'])
def getAllWriters(request):
    writers=Account.objects.filter(is_staff=True,is_superadmin=False).order_by('id')
    serializer=UserSerializer(writers,many=True)
    return Response(serializer.data)




                  
#admin home page
from django.db.models.functions.datetime import ExtractMonth
from django.db.models import Count
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def adminHomePage(request):
    total_users=Account.objects.filter(is_staff=False,is_superadmin=False).count()
    total_writers = Account.objects.filter(is_staff=True,is_superadmin=False).count()
    total_blogs = Blog.objects.all().count()
    monthly_users = Account.objects.annotate(month=ExtractMonth('date_joined')).values('month').annotate(count=Count('id')).values('month','count').exclude(is_superadmin=False)
    datas=[]
    
    for x in monthly_users:
        data = {}
        data.update({'month':calendar.month_name[x['month']]})
        data.update({'users':x['count']})
        datas.append(data)
    
    monthly_blogs = Blog.objects.annotate(month=ExtractMonth('created_at')).values('month').annotate(count=Count('id')).values('month','count')
    blogs=[]
    for x in monthly_blogs:
        blog={}
        blog.update({'month':calendar.month_name[x['month']]})
        blog.update({'blogs':x['count']})
        blogs.append(blog)
    active_users = Account.objects.filter(is_active=True,is_superadmin=False).count()
    non_active_users = Account.objects.filter(is_active=False).count()
    blocked_blogs = Blog.objects.filter(is_blocked=True).count()
    context = {
        'total_users':total_users,
        'total_writers':total_writers,
        'total_blogs':total_blogs,
         'chart':datas,
         'blogs':blogs,
         'active_users':active_users,
         'non_active_users':non_active_users,
         'blocked_blogs':blocked_blogs,
    }
    return Response(context)
    
# fetch all comments by admin
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def AllComments(request):
    comments=Comments.objects.all().order_by('id')
    serializer = AdminPanelCommentSerializer(comments,many=True)
    return Response(serializer.data)

# block or unblock comment by admin
@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def BlockOrUnblockComment(request,id):
    comment=get_object_or_404(Comments,id=id)
    if comment.is_blocked==False:
        comment.is_blocked=True
        comment.save()
        return Response('Blocked')
    else:
        comment.is_blocked=False
        comment.save()
        return Response('Unblocked')

# admin search users
class SearchAccountListView(generics.ListAPIView):
    # permission_classes=[IsAuthenticated]
    queryset = Account.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['first_name','last_name']

# getting data of user for is authenticated or not.
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def IsAuthUser(request,id):
    author=0
    try:
        blog=Blog.objects.get(id=id)
        author=blog.author
    except:
        user=Account.objects.get(id=id)
        blog=Blog.objects.filter(author=user)[:1]
        for i in blog:
            author=i.author
    user=request.user
    if author==user:
        try:
            is_liked=Likes.objects.get(from_user=user)
            is_liked=True
        except:
            is_liked=False
        return Response({'is_author':True},status=status.HTTP_200_OK)
    else:
        try:
            is_follow=Follower.objects.get(user_from=user,user_to=author)
            is_follow=True
        except:
            is_follow=False
        try:
            is_liked=Likes.objects.get(from_user=user,to_blog=blog)
            is_liked=True
        except:
            is_liked=False
        return Response({'is_liked':is_liked,'is_followed':is_follow},status=status.HTTP_202_ACCEPTED)







        



