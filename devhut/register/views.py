
from  rest_framework.decorators import api_view
from rest_framework.response import Response
# customising token claims
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from . models import Account
from . serializer import  UserSerializer, VerifySerializer
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from. import verify
#forgot email
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator   
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from devhut import settings
from django.core.mail import send_mail
from rest_framework import status
from rest_framework import status


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
     @classmethod
     def get_token(cls, user):
        token = super().get_token(user)
        token['is_staff'] = user.is_staff
        token['is_super_admin'] = user.is_superadmin
        if user.is_active == True:
            return token
        else:
            return Response('The user is not active')
    

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(['POST'])
def RegisterUser(request):
    data=request.data
    email=data['email']
    phone_number=data['phone_number']
    if Account.objects.filter(email=email):
        return Response('Email account already exists',status=status.HTTP_202_ACCEPTED)
    elif Account.objects.filter(phone_number=phone_number):
        return Response('Phone number already exists',status=status.HTTP_202_ACCEPTED)
    else:
        user = Account.objects.create(first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone_number=data['phone_number'],
        password=make_password(data['password']),
    )
    phone_number=data['phone_number']
    verify.send(phone_number)
    serializer=VerifySerializer(data)
    return Response(serializer.data)

# verify the otp code 
@api_view(['POST'])
def VerifyCode(request):
    data=request.data
    code = data['code']
    try:
        phone_number = data['phone_number']
        user=Account.objects.get(phone_number=phone_number)
       
        if verify.check(phone_number,code):
            user.is_active=True
            user.save()
            return Response({'Success':'Success'})
        
        else:
            return Response({'error':'Invalid OTP, Please try again'})
    except:
        return Response({'error':'Something goes wrong.'},status=status.HTTP_202_ACCEPTED)
# forgot password function
@api_view(['POST'])
def forgotPassword(request):
    data=request.data
    print(data,'dataaa')
    email=data['email']
    
    if Account.objects.filter(email__iexact=email).exists():
        user=Account.objects.get(email__iexact=email)
        # current_site=get_current_site(request)
        current_site = 'http://localhost:3000'
        mail_subject='Reset your password'
        message = render_to_string('user/reset_password_email.html',{
            'user':user,
            'domain':current_site,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':default_token_generator.make_token(user),
        })
        try:
            send_mail(mail_subject,message,settings.EMAIL_HOST_USER,[email],fail_silently=False)
            
            return Response({'success':'An email sent to you,Please check'})
        except:
            return Response({'error':'Something goes wrong,Please try again'},status=status.HTTP_202_ACCEPTED)
    else:
         return Response({'error':'Sorry,There is no account existing for this email.'},status=status.HTTP_202_ACCEPTED)

@api_view(['POST'])
def resetPassword(request,uidb64,token):
    data=request.data
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except:
        return Response('Something goes wrong, Please try again')
    if not user:
        return Response('Something fishy')
    elif default_token_generator.check_token(user,token):
        password=data['password']
        confirm_password=data['confirm_password']
        uid = urlsafe_base64_decode(uidb64).decode()
        if password==confirm_password:
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            return Response({'success':'Password changed successfully.'},status=status.HTTP_200_OK)
        else:
            return Response({'error':'The password in not matching..'},status=status.HTTP_202_ACCEPTED)
    else:
        return Response({'error':'Invalid token or User'},status=status.HTTP_202_ACCEPTED)
        
    
    






        

