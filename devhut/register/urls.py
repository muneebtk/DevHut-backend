from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,TokenRefreshView
)


urlpatterns=[
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('user/login/',views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/signup/',views.RegisterUser,name='signup'),
    path('user/verify/',views.VerifyCode,name='verify_code'),
    path('user/forgot_password/',views.forgotPassword),
    path('user/reset_password/<uidb64>/<token>/',views.resetPassword,name='reset_password'),
]
