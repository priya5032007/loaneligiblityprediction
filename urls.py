from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.intro, name='intro'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('bank/', views.bank, name='bank'),
    path('predict/', views.predict, name='predict'),
    path('about/', views.about, name='about'),
]
