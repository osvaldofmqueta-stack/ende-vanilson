from django.db import models
from clientes.models import Cliente

class RelatorioGerado(models.Model):
    TIPO_RELATORIO_CHOICES = [
        ('CLIENTES_ATIVOS', 'Clientes Ativos/Inativos'),
        ('CONSUMO_AREA', 'Consumo Médio por Área'),
        ('PAGAMENTOS', 'Pagamentos Recebidos/Pendentes'),
        ('RECLAMACOES', 'Reclamações'),
        ('FINANCEIRO_DIARIO', 'Financeiro Diário'),
        ('FINANCEIRO_MENSAL', 'Financeiro Mensal'),
        ('CONSUMO_MENSAL', 'Consumo Mensal Detalhado'),
    ]
    
    titulo = models.CharField(max_length=200)
    tipo_relatorio = models.CharField(max_length=30, choices=TIPO_RELATORIO_CHOICES)
    periodo_inicio = models.DateField()
    periodo_fim = models.DateField()
    arquivo_pdf = models.FileField(upload_to='relatorios/', null=True, blank=True)
    data_geracao = models.DateTimeField(auto_now_add=True)
    gerado_por = models.CharField(max_length=200)
    observacoes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Relatório Gerado'
        verbose_name_plural = 'Relatórios Gerados'
        ordering = ['-data_geracao']
    
    def __str__(self):
        return f"{self.tipo_relatorio} - {self.data_geracao.strftime('%d/%m/%Y')}"
