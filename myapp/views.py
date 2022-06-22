from django.shortcuts import render
from .serializers import*
from .models import*
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import*
import jwt
from rest_framework.permissions import *
from rest_framework import status
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from .utils import*

# Create your views here.

@api_view(['GET'])
def index(request):
    api_url={
        '':'index/',
        'register':'/register/',
        'login':'/login/',
        'edit-profile':'/edit-profile/',
    }
    return Response(api_url)

class LoginView(GenericAPIView):
    serializer_class=LoginSerializer
    
    def post(self,request,*args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        if serializer.is_valid(raise_exception=True):
            username = request.data['username']
            password = request.data['password']
            user1 = User.objects.get(username=username)
            if user1 is not None:
                try:
                    user = authenticate(request, username=user1.username, password=password)
                    if user is None:
                        return Response(data={"status": status.HTTP_400_BAD_REQUEST, 'error':True, 'message': "Invalid email or password"},status=status.HTTP_400_BAD_REQUEST)
                except:
                    return Response(data={"status": status.HTTP_400_BAD_REQUEST, 'error':True, 'message': "Invalid email or password"},status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, 'error':True, 'message': "Invalid email or password"},status=status.HTTP_400_BAD_REQUEST)
        if user:
            if user:
                payload = {
                    'id': user.id,
                    'email': user.email,
                }
                jwt_token = {'token': jwt.encode(payload, "SECRET_KEY",algorithm='HS256')}
                UserToken.objects.create(user=user, token=jwt_token)
                return Response(data={"status": status.HTTP_200_OK,
                                    "error": False,
                                    "message": "User Login Successfully.",
                                        "result": {'id': user.id,
                                                'email':user.email, 
                                                'token': jwt_token,
                                                }},)
            return Response('user not valid')
        return Response({'msg':'not valid','data':serializer.errors})
    
class UserCreateView(GenericAPIView):
    serializer_class=CreateUserSerializer
    queryset=User.objects.all()
    
    def post(self,request):
        serializer=CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':status.HTTP_200_OK,'msg':'your account created','data':serializer.data})
        else:
            print(serializer.errors)
            return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'enter the valid data'})
        
class EditProfileView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=EditUserSerializer
    
    def get(self,request):
        user=User.objects.get(id=request.user.id)
        serializer=EditUserSerializer(user)
        return Response(serializer.data)
    
    def put(self,request):
        user=User.objects.get(id=request.user.id)
        serializer=EditUserSerializer(instance=user,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':status.HTTP_200_OK,'msg':'your account update','data':serializer.data})
        else:
            return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'enter the valid data'})
            

        