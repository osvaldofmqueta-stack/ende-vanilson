from django.contrib import admin
from .models import Cliente, Contrato, Perfil

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo_usuario', 'telefone')
    list_filter = ('tipo_usuario',)
    search_fields = ('user__username', 'user__email')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['numero_cliente', 'nome', 'nif', 'tipo_cliente', 'status', 'saldo_atual', 'data_cadastro']
    list_filter = ['tipo_cliente', 'status', 'data_cadastro']
    search_fields = ['numero_cliente', 'nome', 'nif', 'bi', 'telefone', 'email']
    readonly_fields = ['numero_cliente', 'data_cadastro', 'data_atualizacao']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('numero_cliente', 'nome', 'nif', 'bi')
        }),
        ('Contacto', {
            'fields': ('morada', 'telefone', 'email')
        }),
        ('Tipo e Status', {
            'fields': ('tipo_cliente', 'status', 'saldo_atual')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Datas', {
            'fields': ('data_cadastro', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ['codigo_contrato', 'cliente', 'status', 'tarifa_kwh', 'data_inicio', 'data_fim']
    list_filter = ['status', 'data_inicio']
    search_fields = ['codigo_contrato', 'cliente__nome', 'cliente__numero_cliente']
    readonly_fields = ['codigo_contrato', 'data_criacao']
    raw_id_fields = ['cliente']
