from django.urls import path
from . import views

urlpatterns = [
    path('', views.contador_list, name='contador_list'),
    path('novo/', views.contador_create, name='contador_create'),
    path('editar/<int:pk>/', views.contador_update, name='contador_update'),
    path('historico/<int:pk>/', views.contador_historico, name='contador_historico'),
    path('leitura/<int:pk>/', views.contador_registrar_leitura, name='contador_registrar_leitura'),
    path('avariado/<int:pk>/', views.contador_marcar_avariado, name='contador_marcar_avariado'),
    path('toggle-status/<int:pk>/', views.contador_toggle_status, name='contador_toggle_status'),
]