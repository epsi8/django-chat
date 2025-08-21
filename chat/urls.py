from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('u/<str:username>/', views.room, name='room'),
    path('api/users/', views.users_status, name='users_status'),
    path('api/heartbeat/', views.heartbeat, name='heartbeat'),
    path('api/history/<int:conversation_id>/', views.history, name='history'),
]
