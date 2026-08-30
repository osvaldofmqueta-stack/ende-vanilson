from django import forms
from .models import Contador
from clientes.models import Cliente

class ContadorForm(forms.ModelForm):
    class Meta:
        model = Contador
        fields = ['numero_serie', 'cliente', 'tipo_conexao', 'numero_cartao', 'endereco_instalacao', 'data_instalacao', 'status', 'potencia_maxima', 'observacoes']
        widgets = {
            'numero_serie': forms.TextInput(attrs={'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'tipo_conexao': forms.Select(attrs={'class': 'form-control'}),
            'numero_cartao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número do cartão do cliente pago'}),
            'endereco_instalacao': forms.TextInput(attrs={'class': 'form-control'}),
            'data_instalacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'potencia_maxima': forms.NumberInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.filter(status='ATIVO').order_by('nome')
        self.fields['cliente'].empty_label = 'Selecionar cliente pago...'
        self.fields['numero_cartao'].required = False

    def clean_cliente(self):
        return self.cleaned_data.get('cliente')

    def clean(self):
        cleaned_data = super().clean()
        cliente = cleaned_data.get('cliente')
        numero_cartao = cleaned_data.get('numero_cartao')
        if cliente and cliente.tipo_cliente == 'PRE_PAGO' and not numero_cartao:
            self.add_error('numero_cartao', 'Informe o número do cartão para um contador de cliente pago.')
        return cleaned_data
