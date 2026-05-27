from django.core.management.base import BaseCommand
from django.utils import timezone
from pagamentos.models import Fatura
from equipamentos.models import Contador
from django.db.models import Q

class Command(BaseCommand):
    help = 'Suspende automaticamente contadores com faturas vencidas há mais de 30 dias'

    def handle(self, *args, **options):
        hoje = timezone.now().date()
        limite_vencimento = hoje - timezone.timedelta(days=30)
        
        # Busca faturas vencidas há mais de 30 dias que ainda não foram pagas
        faturas_atrasadas = Fatura.objects.filter(
            status__in=['PENDENTE', 'VENCIDO'],
            data_vencimento__lt=limite_vencimento
        ).select_related('contador')
        
        contadores_suspensos = 0
        
        for fatura in faturas_atrasadas:
            # Cálculo de multas e juros
            dias_atraso = (hoje - fatura.data_vencimento).days
            if dias_atraso > 0:
                # Exemplo: 2% de multa fixa + 0.1% de juros ao dia
                fatura.multa_atraso = fatura.valor_consumo * timezone.Decimal('0.02')
                fatura.juros_mora = fatura.valor_consumo * timezone.Decimal('0.001') * dias_atraso
                fatura.valor_total = fatura.valor_consumo + fatura.outras_taxas + fatura.multa_atraso + fatura.juros_mora
                fatura.status = 'VENCIDO'
                fatura.save()

            if fatura.contador and fatura.contador.status != 'SUSPENSO':
                fatura.contador.status = 'SUSPENSO'
                fatura.contador.data_suspensao = timezone.now()
                fatura.contador.save()
                contadores_suspensos += 1
                self.stdout.write(self.style.SUCCESS(f'Contador {fatura.contador.numero_serie} suspenso por dívida na fatura {fatura.numero_fatura}'))
        
        self.stdout.write(self.style.SUCCESS(f'Processamento concluído. {contadores_suspensos} contadores suspensos.'))
