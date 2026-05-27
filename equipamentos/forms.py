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
            'numero_cartao': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número do cartão pré-pago'}),
            'endereco_instalacao': forms.TextInput(attrs={'class': 'form-control'}),
            'data_instalacao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'potencia_maxima': forms.NumberInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.filter(tipo_cliente='PRE_PAGO')
        self.fields['cliente'].empty_label = 'Selecionar cliente pré-pago...'
        self.fields['numero_cartao'].required = True

    def clean_cliente(self):
        cliente = self.cleaned_data.get('cliente')
        if cliente and cliente.tipo_cliente != 'PRE_PAGO':
            raise forms.ValidationError(
                f'O cliente "{cliente.nome}" é pós-pago. Apenas clientes pré-pagos podem ser associados a contadores.'
            )
        return cliente

    def clean(self):
        cleaned_data = super().clean()
        numero_cartao = cleaned_data.get('numero_cartao')
        if not numero_cartao:
            self.add_error('numero_cartao', 'O número do cartão é obrigatório para contadores pré-pagos.')
        return cleaned_data
