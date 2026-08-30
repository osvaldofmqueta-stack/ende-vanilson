from django import apps
from django import forms
from .models import Tarifa, Fatura, Pagamento, Recarga
from clientes.models import Cliente

class FaturaSimplesForm(forms.ModelForm):
    class Meta:
        model = Fatura
        fields = ['cliente', 'contador', 'periodo_referencia', 'leitura_anterior', 'leitura_atual', 'status', 'data_emissao', 'data_vencimento']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'contador': forms.Select(attrs={'class': 'form-control'}),
            'periodo_referencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Janeiro/2025'}),
            'leitura_anterior': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'leitura_atual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'data_emissao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'data_vencimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.filter(tipo_cliente='POS_PAGO', status='ATIVO')
        self.fields['cliente'].empty_label = 'Selecionar cliente pós-pago...'

    def clean_cliente(self):
        cliente = self.cleaned_data.get('cliente')
        if cliente and cliente.tipo_cliente != 'POS_PAGO':
            raise forms.ValidationError(
                f'O cliente "{cliente.nome}" é pré-pago. Faturas são exclusivas para clientes pós-pagos.'
            )
        return cliente

class TarifaForm(forms.ModelForm):
    class Meta:
        model = Tarifa
        fields = ['nome', 'tipo', 'preco_kwh', 'taxa_fixa', 'preco_cliente_pos', 'preco_cliente_pre', 'descricao', 'ativa']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'preco_kwh': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'taxa_fixa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'preco_cliente_pos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'preco_cliente_pre': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class PagamentoForm(forms.ModelForm):
    class Meta:
        model = Pagamento
        fields = ['valor_pago', 'metodo_pagamento', 'referencia_multicaixa', 'observacoes']
        widgets = {
            'valor_pago': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Valor pago em Kz'}),
            'metodo_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'referencia_multicaixa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 1234567890'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações (opcional)'}),
        }


class RecargaForm(forms.ModelForm):
    class Meta:
        model = Recarga
        fields = ['cliente', 'valor', 'metodo_pagamento', 'referencia_pagamento', 'observacoes']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'valor': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01', 'placeholder': 'Valor da recarga em Kz'}),
            'metodo_pagamento': forms.Select(attrs={'class': 'form-control'}),
            'referencia_pagamento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Referência ou comprovativo'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Observações (opcional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.filter(
            tipo_cliente='PRE_PAGO',
            status='ATIVO',
        ).order_by('nome')
        self.fields['cliente'].empty_label = 'Selecionar cliente pré-pago...'

    def clean_valor(self):
        valor = self.cleaned_data['valor']
        if valor <= 0:
            raise forms.ValidationError('O valor da recarga deve ser superior a zero.')
        return valor
