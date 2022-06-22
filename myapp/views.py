from ast import For
from django.shortcuts import render
from .serializers import*
from .models import*
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import*
import jwt
from rest_framework.permissions import *
from rest_framework import status
from django.contrib.auth import authenticate,logout
from django.contrib.auth.hashers import make_password
from .utils import*
import random
from django.conf import settings
from django.core.mail import send_mail

@api_view(['GET'])
def index(request):
    api_url={
        '':'index/',
        'register':'/register/',
        'login':'/login/',
        'logout':'/logout/',
        'edit-profile':'/edit-profile/',
        'delete-profile':'/delete-profile/',
        'app-post':'/add-post/',
        'edit-post':'/edit-post/post.id',
        'delete-post':'/delete-post/post.id',
        'my-post':'/my-post/',
        'one-post':'/one-post/post.id',
        'like-post':'/like-post/post-id',
        'unlike-post':'/unlike-post/post-id',
        'comment':'/comment/post.id',
        'mypost-comment':'/mypost-comment/post.id',
        'delete-comment':'/delete-comment/comment.id',
        'following':'/following/user.id',
        'unfollow':'/unfollow/user.id',
        'remove-follower':'/remove-follower/user.id',
        'following-list':'/following-list/',
        'follower-list':'/follower-list/',
        'forgot-password':'/forgot-password/',
        'change-password':'/change-password/',
    }
    return Response(api_url)

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> login/logout/register >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class LoginView(GenericAPIView):
    serializer_class=LoginSerializer
    
    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        if serializer.is_valid():
            username=serializer.validated_data.get('username')
            password=serializer.validated_data.get('password')
            user = authenticate(request, username=username, password=password)
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
        

class LogoutView(GenericAPIView):
    permission_classes=[IsAuthenticated]

    def get(self, request):
        try:
            token = Authenticate(self, request)
            try:
                user_token = UserToken.objects.get(user=request.user)
                user_token.delete()
                logout(request)
            except:
                return Response(data={"Status": status.HTTP_400_BAD_REQUEST,
                                      "Message": 'Already Logged Out.'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(data={"Status": status.HTTP_200_OK,
                                  "Message": "User Logged Out."},
                            status=status.HTTP_200_OK)
        except:
            return Response(data={"Status":status.HTTP_400_BAD_REQUEST,
                                    "Message":'Already Logged Out.'},
                            status=status.HTTP_400_BAD_REQUEST)
            
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> profile-edit-delete >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

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
        
class DeleteProfileView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        user=User.objects.get(id=request.user.id)
        serializer=EditUserSerializer(user)
        return Response(serializer.data)
    
    def delete(self,request):
        user=User.objects.get(id=request.user.id)
        user.delete()
        return Response({'status':status.HTTP_200_OK,'msg':'your account deleted'})
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>forgot-password>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class ForgotPasswordView(GenericAPIView):
    serializer_class=ForgotPasswordSerializers
    
    def post(self,request):
        serializer=ForgotPasswordSerializers(data=request.data)
        if serializer.is_valid():
            email=serializer.validated_data.get('email')
            if User.objects.filter(email=email).exists():
                user=User.objects.get(email=email)
                password=''.join(random.choices('qwyertovghlk34579385',k=8))
                subject="Rest Password"
                message = f"""Hello {user.email},Your New password is {password}"""
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user.email,]
                send_mail( subject, message, email_from, recipient_list )
                user.password=make_password(password)
                user.save()
                return Response('your new password send')
            else:
                return Response('this email is not register')
        else:
            print(serializer.errors)
            return Response('enter the valid data')
        

class ChangePasswordView(GenericAPIView):
    serializer_class=ChangePasswordSerializers
    permission_classes=[IsAuthenticated]
    
    def put(self,request):
        user=User.objects.get(id=request.user.id)
        serializer=ChangePasswordSerializers(instance=user,data=request.data)
        if serializer.is_valid():
            password=serializer.validated_data.get('password')
            serializer.save(password=make_password(password))
            return Response('your password change')
        else:
            return Response('enter the valid data')
        
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> POST >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class CreatePostView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=CreatePostSerializer 
    
    def post(self,request):
        serializer=CreatePostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user) 
            return Response({'status':status.HTTP_200_OK,'msg':'you post successfully','data':serializer.data})
        return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'please enter the valid data'})  
    
class EditPostView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=EditPostSerializer
    
    def put(self,request,pk):
        uid=Post.objects.get(id=pk)
        if uid.user == request.user:
            serializer=EditPostSerializer(instance=uid,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'status':status.HTTP_200_OK,'msg':'your post update'})
            return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'please enter the valid data'})
        return Response('you cannot edit other user post')
        
    
class DeletePostView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    
    
    def get_object(self, pk):
        try:
            return Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            raise Http404 
    
    def delete(self,request,pk):
        post=self.get_object(pk=pk)
        if post.user == request.user:
            post.delete()
            return Response({'status':status.HTTP_200_OK,'msg':'your post delete'})
        return Response('you cannot delete other user post')
    
class MyPostView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=MyPostSerializer
    
    def get(self,request):
        post=Post.objects.filter(user=request.user)
        serializer=MyPostSerializer(post,many=True)
        return Response(serializer.data)
    
class OnePostView(RetrieveAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=MyPostSerializer
    queryset=Post.objects.all()
            
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Likes >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class LikePostView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    
    def post(self,request,pk):
        post=Post.objects.get(id=pk)
        post.likes.add(request.user)
        post.save()
        return Response('you like this post')
    
class UnlikePostView(GenericAPIView):
    permission_classes=[IsAuthenticated]
      
    def post(self,request,pk):
        post=Post.objects.get(id=pk)
        post.likes.remove(request.user)
        post.save()
        return Response('you remove your like for this post')

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Comment>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class CommentPostView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=CommentSerializer
    
    def post(self,request,pk):
        post=Post.objects.get(id=pk)
        serializer=CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user,post=post)
            return Response({'status':status.HTTP_200_OK,'msg':'you comment on this post','data':serializer.data})
        else:
            return Response({'status':status.HTTP_200_OK,'msg':'please enter the valid data'})
        
class ViewPostCommentView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=ViewCommentSerializer
    
    def get(self,request,pk):
        post=Post.objects.get(id=pk)
        comment=Comment.objects.filter(post=post)[::-1]
        com=Comment.objects.filter(post=post).count()
        serializer=ViewCommentSerializer(comment,many=True)
        return Response({'dtat':serializer.data,'total-comment':com})        

class DeleteCommentView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise Http404 
    
    def delete(self,request,pk):
        uid=self.get_object(pk=pk)
        if uid.user == request.user:
            uid.delete()
            return Response('comment deleted')   
        else:
            return Response('you cannot delete other user comment') 

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> follow-unfollow >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class FollowingView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request,pk):
        user=User.objects.get(id=pk)
        if user == request.user:
            return Response('you not following your account')
        else:
            user.followers.add(request.user)
            user.save()
            request.user.following.add(user)
            request.user.save()
            return Response('you following this user')
        
class UnfollowView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request,pk):
        user=User.objects.get(id=pk)
        user.followers.remove(request.user)
        user.save()
        request.user.following.remove(user)
        request.user.save()
        return Response('you unfollow this user')
    
class RemoveFollowerView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request,pk):
        uid=User.objects.get(id=pk)
        request.user.followers.remove(uid)
        request.user.save()
        uid.following.remove(request.user)
        uid.save()
        return Response('you remove this user from you follower list')

class FollowingListView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        user=request.user
        following=user.following.all()
        return Response({'data':following})
    
class FollowerListView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        user=request.user
        following=user.follower.all()
        return Response({'data':following})
    
   