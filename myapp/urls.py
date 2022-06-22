from django.urls import path
from .views import*

urlpatterns = [
    path('',index,name='index'),
    path('login/',LoginView.as_view()),
    path('logout/',LogoutView.as_view()),
    path('register/',UserCreateView.as_view()),
    path('edit-profile/',EditProfileView.as_view()),
    path('delete-profile/',DeleteProfileView.as_view()),
    
    path('add-post/',CreatePostView.as_view()),
    path('edit-post/<int:pk>',EditPostView.as_view()),
    path('delete-post/<int:pk>',DeletePostView.as_view()),
    path('my-post/',MyPostView.as_view()),
    path('one-post/<int:pk>',OnePostView.as_view()),
    
    path('like-post/<int:pk>',LikePostView.as_view()),
    path('unlike-post/<int:pk>',UnlikePostView.as_view()),
    
    path('comment/<int:pk>',CommentPostView.as_view()),
    path('mypost-comment/<int:pk>',ViewPostCommentView.as_view()),
    path('delete-comment/<int:pk>',DeleteCommentView.as_view()),
    
    path('following/<int:pk>',FollowingView.as_view()),
    path('unfollow/<int:pk>',UnfollowView.as_view()),
    path('remove-follower/<int:pk>',RemoveFollowerView.as_view()),
    
    path('following-list/',FollowingListView.as_view()),
    path('follower-list/',FollowerListView.as_view()),
    
    path('forgot-password/',ForgotPasswordView.as_view()),
    path('change-password/',ChangePasswordView.as_view()),
    
    
]