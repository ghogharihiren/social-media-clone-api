from django.urls import path
from .views import*

urlpatterns = [
    path('',index,name='index'),
    path('login/',LoginView.as_view()),
    path('register/',UserCreateView.as_view()),
    path('edit-profile/',EditProfileView.as_view()),
]