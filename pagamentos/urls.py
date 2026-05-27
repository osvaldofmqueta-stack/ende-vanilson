from django.urls import path
from . import views

urlpatterns = [
    path('faturas/', views.fatura_list, name='fatura_list'),
    path('faturas/<int:pk>/', views.fatura_detail, name='fatura_detail'),
    path('faturas/<int:pk>/pdf/', views.fatura_pdf, name='fatura_pdf'),
    path('faturas/<int:pk>/pagamento/', views.registrar_pagamento, name='registrar_pagamento'),
    path('faturas/novo/', views.fatura_create, name='fatura_create'),
    path('faturas/gerar-auto/', views.gerar_faturas_automaticas, name='gerar_faturas_auto'),
    path('divida/', views.controlo_divida, name='controlo_divida'),
    path('suspensao-automatica/', views.acionar_suspensao_automatica, name='acionar_suspensao_automatica'),
    path('contador/<int:pk>/suspender/', views.suspender_contador, name='suspender_contador'),
    path('contador/<int:pk>/reativar/', views.reativar_contador, name='reativar_contador'),
    path('tarifas/', views.tarifa_list, name='tarifa_list'),
    path('tarifas/novo/', views.tarifa_create, name='tarifa_create'),
    path('tarifas/editar/<int:pk>/', views.tarifa_update, name='tarifa_update'),
]