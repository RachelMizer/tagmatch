# support/urls.py

from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reports/', views.report_list, name='report_list'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('users/', views.user_list, name='user_list'),
    path('users/<str:username>/', views.user_detail, name='user_detail'),
    path('users/<str:username>/change-password/', views.change_password, name='change_password'),
    path('users/<str:username>/toggle-active/', views.toggle_active, name='toggle_active'),
    path('users/<str:username>/toggle-support/', views.toggle_support, name='toggle_support'),
]
