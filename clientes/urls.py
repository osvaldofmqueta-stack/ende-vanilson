from django.urls import path
from . import views

urlpatterns = [
    path('', views.cliente_list, name='cliente_list'),
    path('novo/', views.cliente_create, name='cliente_create'),
    path('editar/<int:pk>/', views.cliente_update, name='cliente_update'),
    path('toggle-status/<int:pk>/', views.cliente_toggle_status, name='cliente_toggle_status'),
    path('perfil/', views.perfil_edit, name='perfil_edit'),
]