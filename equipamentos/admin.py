from django.contrib import admin
from .models import Contador, HistoricoManutencao, CartaoRecarga

@admin.register(Contador)
class ContadorAdmin(admin.ModelAdmin):
    list_display = ['numero_serie', 'tipo_contador', 'cliente', 'status', 'data_instalacao', 'leitura_atual']
    list_filter = ['tipo_contador', 'status', 'data_instalacao']
    search_fields = ['numero_serie', 'cliente__nome', 'endereco_instalacao']
    readonly_fields = ['data_criacao', 'tipo_contador']
    raw_id_fields = ['cliente']
    
    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj and obj.cliente:
            readonly.append('tipo_contador')
        return readonly

@admin.register(HistoricoManutencao)
class HistoricoManutencaoAdmin(admin.ModelAdmin):
    list_display = ['contador', 'tipo_manutencao', 'data_manutencao', 'tecnico_responsavel', 'custo']
    list_filter = ['tipo_manutencao', 'data_manutencao']
    search_fields = ['contador__numero_serie', 'tecnico_responsavel', 'descricao']
    readonly_fields = ['data_criacao']
    raw_id_fields = ['contador']

@admin.register(CartaoRecarga)
class CartaoRecargaAdmin(admin.ModelAdmin):
    list_display = ['codigo_cartao', 'valor', 'status', 'data_criacao', 'data_expiracao', 'cliente_uso']
    list_filter = ['status', 'data_criacao']
    search_fields = ['codigo_cartao', 'cliente_uso__nome']
    raw_id_fields = ['cliente_uso']
