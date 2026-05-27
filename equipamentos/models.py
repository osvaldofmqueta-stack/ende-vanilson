from django.db import models
from clientes.models import Cliente

class Contador(models.Model):
    TIPO_CONTADOR_CHOICES = [
        ('PRE_PAGO', 'Pré-pago'),
        ('POS_PAGO', 'Pós-pago'),
    ]
    
    TIPO_CONEXAO_CHOICES = [
        ('MONOFASICO', 'Monofásico'),
        ('TRIFASICO', 'Trifásico'),
    ]
    
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('INATIVO', 'Inativo'),
        ('MANUTENCAO', 'Em Manutenção'),
        ('AVARIADO', 'Avariado'),
        ('SUBSTITUIDO', 'Substituído'),
        ('SUSPENSO', 'Suspenso por Dívida'),
    ]
    
    numero_serie = models.CharField(max_length=50, unique=True)
    tipo_contador = models.CharField(max_length=10, choices=TIPO_CONTADOR_CHOICES)
    tipo_conexao = models.CharField(max_length=15, choices=TIPO_CONEXAO_CHOICES, default='MONOFASICO')
    numero_cartao = models.CharField(max_length=20, blank=True, null=True, help_text='Número do cartão (apenas para pré-pago)')
    cliente = models.OneToOneField(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='contador')
    endereco_instalacao = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ATIVO')
    data_instalacao = models.DateField()
    data_ultima_leitura = models.DateTimeField(null=True, blank=True)
    leitura_atual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    potencia_maxima = models.DecimalField(max_digits=8, decimal_places=2, help_text='Potência máxima em kW')
    observacoes = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_suspensao = models.DateTimeField(null=True, blank=True, help_text='Data da suspensão por dívida')
    
    class Meta:
        verbose_name = 'Contador'
        verbose_name_plural = 'Contadores'
        ordering = ['-data_instalacao']
    
    def __str__(self):
        return f"{self.numero_serie} - {self.cliente.nome if self.cliente else 'Sem Cliente'}"
    
    def save(self, *args, **kwargs):
        if self.cliente:
            self.tipo_contador = self.cliente.tipo_cliente
        super().save(*args, **kwargs)


class LeituraConsumo(models.Model):
    contador = models.ForeignKey(Contador, on_delete=models.CASCADE, related_name='leituras')
    leitura_anterior = models.DecimalField(max_digits=10, decimal_places=2)
    leitura_atual = models.DecimalField(max_digits=10, decimal_places=2)
    consumo = models.DecimalField(max_digits=10, decimal_places=2)
    data_leitura = models.DateTimeField(auto_now_add=True)
    operador = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-data_leitura']

    def __str__(self):
        return f"{self.contador.numero_serie} - {self.data_leitura.strftime('%d/%m/%Y')}"


class HistoricoManutencao(models.Model):
    TIPO_MANUTENCAO_CHOICES = [
        ('PREVENTIVA', 'Preventiva'),
        ('CORRETIVA', 'Corretiva'),
        ('SUBSTITUICAO', 'Substituição'),
    ]
    
    contador = models.ForeignKey(Contador, on_delete=models.CASCADE, related_name='historico_manutencao')
    tipo_manutencao = models.CharField(max_length=15, choices=TIPO_MANUTENCAO_CHOICES)
    descricao = models.TextField()
    data_manutencao = models.DateTimeField()
    tecnico_responsavel = models.CharField(max_length=200)
    custo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    observacoes = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Histórico de Manutenção'
        verbose_name_plural = 'Históricos de Manutenção'
        ordering = ['-data_manutencao']
    
    def __str__(self):
        return f"{self.contador.numero_serie} - {self.tipo_manutencao} em {self.data_manutencao.strftime('%d/%m/%Y')}"


class CartaoRecarga(models.Model):
    STATUS_CARTAO_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('USADO', 'Usado'),
        ('EXPIRADO', 'Expirado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    codigo_cartao = models.CharField(max_length=20, unique=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CARTAO_CHOICES, default='ATIVO')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField()
    data_uso = models.DateTimeField(null=True, blank=True)
    cliente_uso = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='cartoes_usados')
    
    class Meta:
        verbose_name = 'Cartão de Recarga'
        verbose_name_plural = 'Cartões de Recarga'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.codigo_cartao} - {self.valor} Kz"
