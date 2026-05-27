from django.contrib import admin
from .models import RelatorioGerado

@admin.register(RelatorioGerado)
class RelatorioGeradoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'tipo_relatorio', 'periodo_inicio', 'periodo_fim', 'data_geracao', 'gerado_por']
    list_filter = ['tipo_relatorio', 'data_geracao']
    search_fields = ['titulo', 'gerado_por']
    readonly_fields = ['data_geracao']
