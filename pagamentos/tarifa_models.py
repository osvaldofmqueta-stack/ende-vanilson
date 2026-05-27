from django.db import models

class Tarifa(models.Model):
    TIPO_TARIFA_CHOICES = [
        ('DOMESTICA', 'Doméstica'),
        ('COMERCIAL', 'Comercial'),
        ('INDUSTRIAL', 'Industrial'),
    ]
    
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_TARIFA_CHOICES, default='DOMESTICA')
    preco_kwh = models.DecimalField(max_digits=10, decimal_places=2, help_text="Preço por kWh em Kz")
    taxa_fixa = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Taxa fixa mensal em Kz")
    preco_cliente_pos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço p/ Cliente Pós-pago", help_text="Taxa adicional fixa para clientes pós-pagos")
    preco_cliente_pre = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço p/ Cliente Pré-pago", help_text="Taxa adicional fixa para clientes pré-pagos")
    descricao = models.TextField(blank=True, null=True, help_text="Descrição simples do plano/tarifa")
    ativa = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Plano de Tarifa'
        verbose_name_plural = 'Planos de Tarifas'

    def __str__(self):
        return f"{self.nome} ({self.preco_kwh} Kz/kWh)"
