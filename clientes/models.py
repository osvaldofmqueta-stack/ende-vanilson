from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
import uuid

class Perfil(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('OPERADOR', 'Operador'),
        ('FINANCEIRO', 'Financeiro'),
        ('CLIENTE', 'Cliente'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='CLIENTE')
    telefone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_tipo_usuario_display()}"

class Cliente(models.Model):
    TIPO_CLIENTE_CHOICES = [
        ('PRE_PAGO', 'Pré-pago'),
        ('POS_PAGO', 'Pós-pago'),
    ]
    
    STATUS_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('INATIVO', 'Inativo'),
        ('SUSPENSO', 'Suspenso'),
    ]
    
    numero_cliente = models.CharField(max_length=20, unique=True, editable=False)
    nome = models.CharField(max_length=200)
    nif = models.CharField(max_length=20, unique=True, verbose_name='NIF')
    bi = models.CharField(max_length=20, unique=True, verbose_name='BI')
    morada = models.TextField()
    telefone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Número de telefone inválido")]
    )
    email = models.EmailField(blank=True, null=True)
    tipo_cliente = models.CharField(max_length=10, choices=TIPO_CLIENTE_CHOICES, default='PRE_PAGO')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ATIVO')
    saldo_atual = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tarifa = models.ForeignKey('pagamentos.Tarifa', on_delete=models.SET_NULL, null=True, blank=True, related_name='clientes')
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['-data_cadastro']
    
    def __str__(self):
        return f"{self.numero_cliente} - {self.nome}"
    
    def save(self, *args, **kwargs):
        if not self.numero_cliente:
            ultimo_numero = Cliente.objects.all().order_by('-id').first()
            if ultimo_numero:
                numero = int(ultimo_numero.numero_cliente.split('-')[1]) + 1
            else:
                numero = 1
            self.numero_cliente = f"CLI-{numero:06d}"
        super().save(*args, **kwargs)


class Contrato(models.Model):
    STATUS_CONTRATO_CHOICES = [
        ('ATIVO', 'Ativo'),
        ('CANCELADO', 'Cancelado'),
        ('SUSPENSO', 'Suspenso'),
    ]
    
    codigo_contrato = models.CharField(max_length=30, unique=True, editable=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='contratos')
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CONTRATO_CHOICES, default='ATIVO')
    tarifa_kwh = models.DecimalField(max_digits=8, decimal_places=2, default=10.00)
    observacoes = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.codigo_contrato} - {self.cliente.nome}"
    
    def save(self, *args, **kwargs):
        if not self.codigo_contrato:
            codigo_unico = str(uuid.uuid4().hex[:8]).upper()
            ano_atual = self.data_inicio.year
            self.codigo_contrato = f"CTR-{ano_atual}-{codigo_unico}"
        super().save(*args, **kwargs)
