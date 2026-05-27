from django.db import models
from .tarifa_models import Tarifa
from clientes.models import Cliente
from equipamentos.models import Contador

class Recarga(models.Model):
    STATUS_RECARGA_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('CONFIRMADO', 'Confirmado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    METODO_PAGAMENTO_CHOICES = [
        ('MULTICAIXA', 'Multicaixa'),
        ('ATM', 'ATM'),
        ('USSD', 'USSD'),
        ('APP', 'App Mobile'),
        ('CARTAO', 'Cartão de Recarga'),
        ('DINHEIRO', 'Dinheiro'),
    ]
    
    numero_recarga = models.CharField(max_length=30, unique=True, editable=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='recargas')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pagamento = models.CharField(max_length=15, choices=METODO_PAGAMENTO_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_RECARGA_CHOICES, default='PENDENTE')
    referencia_pagamento = models.CharField(max_length=100, blank=True, null=True)
    data_recarga = models.DateTimeField(auto_now_add=True)
    data_confirmacao = models.DateTimeField(null=True, blank=True)
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Recarga'
        verbose_name_plural = 'Recargas'
        ordering = ['-data_recarga']
    
    def __str__(self):
        return f"{self.numero_recarga} - {self.cliente.nome} - {self.valor} Kz"
    
    def save(self, *args, **kwargs):
        if not self.numero_recarga:
            import uuid
            codigo = str(uuid.uuid4().hex[:6]).upper()
            self.numero_recarga = f"REC-{codigo}"
        super().save(*args, **kwargs)


class Fatura(models.Model):
    STATUS_FATURA_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PAGO', 'Pago'),
        ('VENCIDO', 'Vencido'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    numero_fatura = models.CharField(max_length=30, unique=True, editable=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='faturas')
    contador = models.ForeignKey(Contador, on_delete=models.SET_NULL, null=True, related_name='faturas')
    periodo_referencia = models.CharField(max_length=50, help_text='Ex: Janeiro/2025')
    leitura_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    leitura_atual = models.DecimalField(max_digits=10, decimal_places=2)
    consumo_kwh = models.DecimalField(max_digits=10, decimal_places=2)
    valor_consumo = models.DecimalField(max_digits=10, decimal_places=2)
    multa_atraso = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text='Multa por atraso (valor fixo)')
    juros_mora = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text='Juros de mora acumulados')
    outras_taxas = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_FATURA_CHOICES, default='PENDENTE')
    data_emissao = models.DateField()
    data_vencimento = models.DateField()
    data_pagamento = models.DateTimeField(null=True, blank=True)
    arquivo_pdf = models.FileField(upload_to='faturas/', null=True, blank=True)
    observacoes = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Fatura'
        verbose_name_plural = 'Faturas'
        ordering = ['-data_emissao']
    
    def __str__(self):
        return f"{self.numero_fatura} - {self.cliente.nome}"
    
    def save(self, *args, **kwargs):
        if not self.numero_fatura:
            import uuid
            from datetime import datetime
            ano = datetime.now().year
            codigo = str(uuid.uuid4().hex[:6]).upper()
            self.numero_fatura = f"FAT-{ano}-{codigo}"
        
        if not self.consumo_kwh:
            self.consumo_kwh = self.leitura_atual - self.leitura_anterior
        
        super().save(*args, **kwargs)


class Recibo(models.Model):
    numero_recibo = models.CharField(max_length=30, unique=True, editable=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='recibos')
    fatura = models.ForeignKey(Fatura, on_delete=models.SET_NULL, null=True, blank=True, related_name='recibos')
    recarga = models.ForeignKey(Recarga, on_delete=models.SET_NULL, null=True, blank=True, related_name='recibos')
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pagamento = models.CharField(max_length=50)
    data_emissao = models.DateTimeField(auto_now_add=True)
    arquivo_pdf = models.FileField(upload_to='recibos/', null=True, blank=True)
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Recibo'
        verbose_name_plural = 'Recibos'
        ordering = ['-data_emissao']
    
    def __str__(self):
        return f"{self.numero_recibo} - {self.cliente.nome}"
    
    def save(self, *args, **kwargs):
        if not self.numero_recibo:
            import uuid
            from datetime import datetime
            ano = datetime.now().year
            codigo = str(uuid.uuid4().hex[:6]).upper()
            self.numero_recibo = f"REC-{ano}-{codigo}"
        super().save(*args, **kwargs)


class Pagamento(models.Model):
    METODO_PAGAMENTO_CHOICES = [
        ('DINHEIRO', 'Dinheiro'),
        ('MULTICAIXA', 'Multicaixa'),
    ]
    
    numero_pagamento = models.CharField(max_length=30, unique=True, editable=False)
    fatura = models.ForeignKey(Fatura, on_delete=models.CASCADE, related_name='pagamentos')
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pagamento = models.CharField(max_length=20, choices=METODO_PAGAMENTO_CHOICES)
    referencia_multicaixa = models.CharField(max_length=100, blank=True, null=True, help_text='Referência da transferência Multicaixa')
    data_pagamento = models.DateTimeField(auto_now_add=True)
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-data_pagamento']
    
    def __str__(self):
        return f"{self.numero_pagamento} - {self.fatura.numero_fatura} - {self.valor_pago} Kz"
    
    def save(self, *args, **kwargs):
        if not self.numero_pagamento:
            import uuid
            from datetime import datetime
            ano = datetime.now().year
            codigo = str(uuid.uuid4().hex[:6]).upper()
            self.numero_pagamento = f"PAG-{ano}-{codigo}"
        
        # Atualizar status da fatura
        if self.valor_pago >= self.fatura.valor_total:
            self.fatura.status = 'PAGO'
            self.fatura.data_pagamento = self.data_pagamento
            self.fatura.save()
        
        super().save(*args, **kwargs)


class Notificacao(models.Model):
    TIPO_CHOICES = [
        ('SALDO_BAIXO', 'Saldo Baixo'),
        ('FATURA_VENCIDA', 'Fatura Vencida'),
        ('PAGAMENTO_CONFIRMADO', 'Pagamento Confirmado'),
        ('MANUTENCAO', 'Manutenção'),
        ('GERAL', 'Geral'),
    ]
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('ENVIADO', 'Enviado'),
        ('ERRO', 'Erro'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='notificacoes')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    mensagem = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_envio = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.tipo} - {self.cliente.nome}"
