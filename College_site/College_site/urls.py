"""
URL configuration for College_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Dashboard import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  
    path('analytics/', views.analytics, name='analytics'),
    path('upload/', views.upload_excel, name='upload'),
    path('students/', views.students_list, name='students'),
    path('export/', views.export_excel, name='export_excel'),
    path('sync/', views.sync_google_forms, name='sync'),
    path('ai/', views.ai_analysis, name='ai'),
    path('groups/', views.groups, name='groups'),
    path('pdf/', views.download_pdf, name='pdf'),
    path("map/", views.map_view, name="map"),
    path("ai-chat/", views.ai_chat, name="ai_chat"),
    path("clear-chat/", views.clear_chat, name="clear_chat"),
]