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
