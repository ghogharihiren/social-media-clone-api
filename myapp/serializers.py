from rest_framework import serializers
from .models import*
from django.contrib.auth.hashers import make_password


class LoginSerializer(serializers.ModelSerializer):
    username=serializers.CharField(max_length=20)
    class Meta:
        model=User
        fields=['username','password']
        
class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['first_name','last_name','username','mobile','email','password','bio']
        
              
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(CreateUserSerializer, self).create(validated_data)
    
class EditUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['first_name','last_name','username','mobile','bio','profile_pic']
        
class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model=Post
        fields=['files','description']
        
class EditPostSerializer(serializers.ModelSerializer):
    class Meta:
        model=Post
        fields=['files','description']
        
class MyPostSerializer(serializers.ModelSerializer):
    class Meta:
        model=Post
        fields='__all__'
        
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Comment
        fields=['comment']
        
class ViewCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Comment
        fields=['id','post','comment','date']

class ForgotPasswordSerializers(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=50)
    class Meta:
        model=User
        fields=['email']
        
class ChangePasswordSerializers(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('old_password', 'password', 'password2')