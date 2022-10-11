from rest_framework import serializers
from django.contrib.auth import get_user_model
from . models import Account
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id','email','is_active','first_name','phone_number','image','about','last_name','is_staff','is_active','is_liked','followers','is_followed']

    def get_name(self,obj):
        name = obj.first_name
        return name

# class UserSerializerWithToken(UserSerializer):
#     name=serializers.SerializerMethodField(read_only=True)
#     token=serializers.SerializerMethodField(read_only=True)
#     class Meta:
#         model = Account
#         fields = ['id','name','email','is_admin','token']

#     def get_token(self,obj):
#         token = RefreshToken.for_user(obj)
#         return str(token.access_token)
#     def get_name(self,obj):
#         name=obj.first_name
#         return name

class VerifySerializer(serializers.ModelSerializer):
    class Meta:
        model=Account
        fields=['phone_number']