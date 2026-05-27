from django.contrib import admin
from .models import Recarga, Fatura, Recibo, Notificacao, Tarifa

@admin.register(Tarifa)
class TarifaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'preco_kwh', 'taxa_fixa', 'ativa')
    list_filter = ('tipo', 'ativa')
    search_fields = ('nome',)

@admin.register(Recarga)
class RecargaAdmin(admin.ModelAdmin):
    list_display = ['numero_recarga', 'cliente', 'valor', 'metodo_pagamento', 'status', 'data_recarga']
    list_filter = ['status', 'metodo_pagamento', 'data_recarga']
    search_fields = ['numero_recarga', 'cliente__nome', 'referencia_pagamento']
    readonly_fields = ['numero_recarga', 'data_recarga']
    raw_id_fields = ['cliente']

@admin.register(Fatura)
class FaturaAdmin(admin.ModelAdmin):
    list_display = ['numero_fatura', 'cliente', 'periodo_referencia', 'valor_total', 'status', 'data_vencimento']
    list_filter = ['status', 'data_emissao', 'data_vencimento']
    search_fields = ['numero_fatura', 'cliente__nome', 'periodo_referencia']
    readonly_fields = ['numero_fatura', 'consumo_kwh', 'data_criacao']
    raw_id_fields = ['cliente', 'contador']

@admin.register(Recibo)
class ReciboAdmin(admin.ModelAdmin):
    list_display = ['numero_recibo', 'cliente', 'valor', 'metodo_pagamento', 'data_emissao']
    list_filter = ['metodo_pagamento', 'data_emissao']
    search_fields = ['numero_recibo', 'cliente__nome']
    readonly_fields = ['numero_recibo', 'data_emissao']
    raw_id_fields = ['cliente', 'fatura', 'recarga']

@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'tipo', 'status', 'data_criacao', 'data_envio']
    list_filter = ['tipo', 'status', 'data_criacao']
    search_fields = ['cliente__nome', 'mensagem']
    raw_id_fields = ['cliente']
