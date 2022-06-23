from django.shortcuts import render
from .serializers import*
from .models import*
from rest_framework.response import Response
from rest_framework.generics import*
import jwt
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth import authenticate,logout
from django.contrib.auth.hashers import make_password
from .utils import*
import random
from django.conf import settings
from django.core.mail import send_mail


class UrlView(GenericAPIView):
    permission_classes=[AllowAny]
    def get(self,request):
        api_url={
            '':'url/',
            'index':'/index/',
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
    

class IndexView(GenericAPIView):
    serializer_class=MyPostSerializer
    
    def get(self,request):
        l=[]
        post=Post.objects.all()
        for i in post:
            if request.user in i.user.followers.all():
                l.append(i)
        pgqs = self.paginate_queryset(self.filter_queryset(l))
        ress = self.get_paginated_response(pgqs)
        count = ress.data['count']
        next_data = ress.data['next']
        previous = ress.data['previous']
        serializer = self.get_serializer(pgqs,many=True)   
        if serializer.data == []:
            return Response({"Status": 404,"Message":"Data not found"})
        return Response({"Status": 200,"Message":"Data found","count":count,"next":next_data,
                        "previous":previous,"Results":serializer.data})
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> login/logout/register >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class LoginView(GenericAPIView):
    permission_classes=[AllowAny]
    
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
                                    "message": "User Login Successfully.",
                                        "result": {'id': user.id,
                                                'email':user.email, 
                                                'token': jwt_token,
                                                }},)
            return Response({'status':status.HTTP_400_BAD_REQUEST,'message':'user not valid'})
        return Response({'status':status.HTTP_404_NOT_FOUND,'message':'Enter the valid data'})
    
class UserCreateView(GenericAPIView):
    permission_classes=[AllowAny]
    
    def post(self,request):
        serializer=CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':status.HTTP_201_CREATED,'message':'your account created','result':serializer.data})
        else:
            print(serializer.errors)
            return Response({'status':status.HTTP_404_NOT_FOUND,'message':'enter the valid data'})
        

class LogoutView(GenericAPIView):

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
    
    def get(self,request):
        user=User.objects.get(id=request.user.id)
        serializer=EditUserSerializer(user)
        return Response({'status':status.HTTP_100_CONTINUE,'message':'your profile','result':serializer.data})
    
    def put(self,request):
        user=User.objects.get(id=request.user.id)
        serializer=EditUserSerializer(instance=user,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':status.HTTP_200_OK,'message':'your account update','result':serializer.data})
        else:
            return Response({'status':status.HTTP_404_NOT_FOUND,'message':'enter the valid data'})
        
class DeleteProfileView(GenericAPIView):
    
    def get(self,request):
        user=User.objects.get(id=request.user.id)
        serializer=EditUserSerializer(user)
        return Response({'status':status.HTTP_100_CONTINUE,'message':'your profile','result':serializer.data})
    
    def delete(self,request):
        user=User.objects.get(id=request.user.id)
        user.delete()
        return Response({'status':status.HTTP_200_OK,'message':'your account deleted'})
    
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> forgot-password >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class ForgotPasswordView(GenericAPIView):
    permission_classes=[AllowAny]

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
                return Response({'status':status.HTTP_200_OK,'message':'new password send in your email',
                                 'result':serializer.data})
            else:
                return Response({'status':status.HTTP_400_BAD_REQUEST,'message':'your email not register'})
        else:
            print(serializer.errors)
            return Response({'status':status.HTTP_404_NOT_FOUND,'message':'please enter the valid data'})
        

class ChangePasswordView(GenericAPIView):
    
    
    def put(self,request):
        user=User.objects.get(id=request.user.id)
        serializer=ChangePasswordSerializers(instance=user,data=request.data)
        if serializer.is_valid():
            password2=serializer.validated_data.get('password2')
            password=serializer.validated_data.get('password')
            if password == password2:
                serializer.save(password=make_password(password))
                return Response({'status':status.HTTP_200_OK,'message':'your password change'})
            else:
                return Response({'status':status.HTTP_400_BAD_REQUEST,'message':'both password not same'})
        else:
            return Response({'status':status.HTTP_404_NOT_FOUND,'message':'please enter the valid data'})
        
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> POST >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class CreatePostView(GenericAPIView):
 
    def post(self,request):
        serializer=CreatePostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user) 
            return Response({'status':status.HTTP_201_CREATED,'message':'you post successfully','result':serializer.data})
        return Response({'status':status.HTTP_404_NOT_FOUND,'message':'please enter the valid data'})  
    
class EditPostView(GenericAPIView):
  
    def put(self,request,pk):
        uid=Post.objects.get(id=pk)
        if uid.user == request.user:
            serializer=EditPostSerializer(instance=uid,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'status':status.HTTP_200_OK,'message':'your post update','result':serializer.data})
            return Response({'status':status.HTTP_404_NOT_FOUND,'message':'please enter the valid data'})
        return Response({'status':status.HTTP_401_UNAUTHORIZED,'message':'you cannot edit other user post'})
        
    
class DeletePostView(GenericAPIView):
  
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
        return Response({'status':status.HTTP_401_UNAUTHORIZED,'message':'you cannot delete other user post'})
    
class MyPostView(GenericAPIView):
    serializer_class=MyPostSerializer
    
    def get(self,request):
        post=Post.objects.filter(user=request.user)
        pgqs = self.paginate_queryset(self.filter_queryset(post))
        ress = self.get_paginated_response(pgqs)
        count = ress.data['count']
        next_data = ress.data['next']
        previous = ress.data['previous']
        serializer = self.get_serializer(pgqs,many=True)   
        if serializer.data == []:
            return Response({"Status": 404,"Message":"Data not found"})
        return Response({"Status": 200,"Message":"Data found","count":count,"next":next_data,
                        "previous":previous,"Results":serializer.data})
       
class OnePostView(GenericAPIView):
    
    def get(self,request,pk):
        post=Post.objects.get(id=pk)
        serializer=MyPostSerializer(post)
        return Response({'status':status.HTTP_100_CONTINUE,'message':'your post','result':serializer.data})
        
        
            
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> Likes >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class LikePostView(GenericAPIView):
    
    def post(self,request,pk):
        post=Post.objects.get(id=pk)
        post.likes.add(request.user)
        post.save()
        return Response({'status':status.HTTP_100_CONTINUE,'message':'you like this post'})
    
class UnlikePostView(GenericAPIView):
   
    def post(self,request,pk):
        post=Post.objects.get(id=pk)
        post.likes.remove(request.user)
        post.save()
        return Response({'status':status.HTTP_100_CONTINUE,'message':'you remove your like for this post'})

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Comment>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class CommentPostView(GenericAPIView):
    
    def post(self,request,pk):
        post=Post.objects.get(id=pk)
        serializer=CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user,post=post)
            return Response({'status':status.HTTP_200_OK,'message':'you comment on this post','result':serializer.data})
        else:
            return Response({'status':status.HTTP_200_OK,'message':'please enter the valid data'})
        
class ViewPostCommentView(GenericAPIView):
    serializer_class=ViewCommentSerializer
    
    def get(self,request,pk):
        post=Post.objects.get(id=pk)
        comment=Comment.objects.filter(post=post)[::-1]
        pgqs = self.paginate_queryset(self.filter_queryset(comment))
        ress = self.get_paginated_response(pgqs)
        count = ress.data['count']
        next_data = ress.data['next']
        previous = ress.data['previous']
        serializer = self.get_serializer(pgqs,many=True)   
        if serializer.data == []:
            return Response({"Status": 404,"Message":"Data not found"})
        return Response({"Status": 200,"Message":"Data found","count":count,"next":next_data,
                        "previous":previous,"Results":serializer.data})
        
class DeleteCommentView(GenericAPIView):
  
    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise Http404 
    
    def delete(self,request,pk):
        uid=self.get_object(pk=pk)
        if uid.user == request.user:
            uid.delete()
            return Response({'status':status.HTTP_100_CONTINUE,'message':'comment deleted'})   
        else:
            return Response({'status':status.HTTP_401_UNAUTHORIZED,'message':'you cannot delete other user comment'}) 

#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> follow-unfollow >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class FollowingView(GenericAPIView):
    
    def get(self,request,pk):
        user=User.objects.get(id=pk)
        if user == request.user:
            return Response({'status':status.HTTP_100_CONTINUE,'message':'you not following your account'})
        else:
            user.followers.add(request.user)
            user.save()
            request.user.following.add(user)
            request.user.save()
            return Response({'status':status.HTTP_100_CONTINUE,'message':'you following this user'})
        
class UnfollowView(GenericAPIView):
    
    def get(self,request,pk):
        user=User.objects.get(id=pk)
        user.followers.remove(request.user)
        user.save()
        request.user.following.remove(user)
        request.user.save()
        return Response({'status':status.HTTP_100_CONTINUE,'message':'you unfollow this user'})
    
class RemoveFollowerView(GenericAPIView):
    
    def get(self,request,pk):
        uid=User.objects.get(id=pk)
        request.user.followers.remove(uid)
        request.user.save()
        uid.following.remove(request.user)
        uid.save()
        return Response({'status':status.HTTP_100_CONTINUE,'message':'you remove this user from you follower list'})

class FollowingListView(GenericAPIView):
   
    def get(self,request):
        user=request.user
        following=user.following.all()
        return Response({'status':status.HTTP_100_CONTINUE,'message':'your following list','result':following})
    
class FollowerListView(GenericAPIView):
    def get(self,request):
        user=request.user
        following=user.follower.all()
        return Response({'status':status.HTTP_100_CONTINUE,'message':'your follower list','result':following})
    
   