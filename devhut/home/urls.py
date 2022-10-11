from django.urls import path
from . import views

urlpatterns = [
    path('blogs/',views.WriteBlogs.as_view()),
    path('',views.all_blogs,name='all_blogs'),
    path('blog_view/<int:id>/',views.CommentList.as_view()),
    path('author/profile/<int:id>/',views.AuthorProfile.as_view()),
    path('blogs/<slug:slug>/',views.categoryView),
    path('edit_author_profile/<int:id>/',views.EditAuthorProfile),
    path('search/',views.SearchBlogListView.as_view()),
    path('following_blogs/',views.followingBlogs),
    path('python_compiler/',views.pythonCompiler),
    path('admin_panel/users/<int:id>/',views.AllUsers.as_view()),
    path('admin_panel/users/',views.getAllUsers),
    path('admin_panel/all_blogs/',views.getAllBlogs),
    path('blogs/edit_blog/<int:id>/',views.EditOrDeleteBlog),
    path('edit_or_delete_comment/<int:id>/',views.EditOrDeleteComment),
    path('blogs_author/<int:id>/',views.IsAuthUser),
    path('admin_panel/block_or_unblock_blog/<int:id>/',views.BlockOrUnBlockBlog),
    path('admin_panel/writers/',views.getAllWriters),
    path('admin_panel/home/',views.adminHomePage),
    path('admin_panel/all_comments/',views.AllComments),
    path('admin_panel/block_or_unblock_comment/<int:id>/',views.BlockOrUnblockComment),
    path('admin_search_users/',views.SearchAccountListView.as_view(),),
]
