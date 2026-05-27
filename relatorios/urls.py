from django.urls import path
from . import views

urlpatterns = [
    path('', views.relatorio_list, name='relatorio_list'),
    path('gerar/', views.gerar_relatorio_view, name='gerar_relatorio'),
    path('estatisticas/', views.estatisticas_gerais, name='estatisticas_gerais'),
    path('exportar/pdf/<int:pk>/', views.exportar_relatorio_pdf, name='exportar_relatorio_pdf'),
    path('exportar/excel/<int:pk>/', views.exportar_relatorio_excel, name='exportar_relatorio_excel'),
]
