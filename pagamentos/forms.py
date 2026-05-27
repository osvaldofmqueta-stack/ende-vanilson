from django import apps
from django import forms
from .models import Tarifa, Fatura, Pagamento

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
