from django.contrib import admin
from django import forms
from .models import Contador, HistoricoManutencao, CartaoRecarga
from clientes.models import Cliente

class ContadorAdminForm(forms.ModelForm):
    class Meta:
        model = Contador
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.filter(tipo_cliente='PRE_PAGO')
        self.fields['cliente'].empty_label = 'Selecionar cliente pago...'

    def clean_cliente(self):
        cliente = self.cleaned_data.get('cliente')
        if cliente and cliente.tipo_cliente != 'PRE_PAGO':
            raise forms.ValidationError(
                f'O cliente "{cliente.nome}" está configurado para faturação. Apenas clientes pagos por recarga podem ser associados a contadores.'
            )
        return cliente

@admin.register(Contador)
class ContadorAdmin(admin.ModelAdmin):
    form = ContadorAdminForm
    list_display = ['numero_serie', 'cliente', 'tipo_cliente_badge', 'status', 'data_instalacao', 'leitura_atual']
    list_filter = ['status', 'data_instalacao']
    search_fields = ['numero_serie', 'cliente__nome', 'endereco_instalacao']
    readonly_fields = ['data_criacao']

    @admin.display(description='Tipo Cliente')
    def tipo_cliente_badge(self, obj):
        if obj.cliente:
            return obj.cliente.get_tipo_cliente_display()
        return '—'

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
