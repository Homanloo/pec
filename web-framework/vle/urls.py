from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('home/', views.home, name="home"),
    path('vle/', views.vle, name="vle"),
    path('pxy/', views.pxy, name="pxy"),
    path('pt/', views.pt, name="pt"),
    path('api/', views.api, name="api"),
    path('docs/', views.docs, name="docs"),
]
