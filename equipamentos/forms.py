from django import forms
from .models import Contador

class ContadorForm(forms.ModelForm):
    class Meta:
        model = Contador
        fields = ['numero_serie', 'cliente', 'tipo_contador', 'tipo_conexao', 'numero_cartao', 'endereco_instalacao', 'data_instalacao', 'status', 'potencia_maxima', 'observacoes']
        widgets = {
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'tipo_contador': forms.Select(attrs={'class': 'form-control'}),
            'tipo_conexao': forms.Select(attrs={'class': 'form-control'}),
            'numero_cartao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Obrigatório para pré-pago'}),
            'endereco_instalacao': forms.TextInput(attrs={'class': 'form-control'}),
            'data_instalacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'potencia_maxima': forms.NumberInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo_contador = cleaned_data.get('tipo_contador')
        numero_cartao = cleaned_data.get('numero_cartao')

        if tipo_contador == 'PRE_PAGO' and not numero_cartao:
            self.add_error('numero_cartao', 'O número do cartão é obrigatório para contadores pré-pagos.')
        
        return cleaned_data