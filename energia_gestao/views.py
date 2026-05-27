from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from clientes.models import Cliente
from equipamentos.models import Contador
from pagamentos.models import Fatura, Recarga
from django.db.models import Sum, Count
from django.utils import timezone

@login_required
def home(request):
    # Todos os utilizadores autenticados são encaminhados directamente para o dashboard
    return redirect('dashboard')

@login_required
def dashboard(request):
    from decimal import Decimal
    SALDO_BAIXO_LIMITE = Decimal('500.00')

    contadores_saldo_baixo = Contador.objects.filter(
        status='ATIVO',
        cliente__isnull=False,
        cliente__saldo_atual__lte=SALDO_BAIXO_LIMITE
    ).select_related('cliente').order_by('cliente__saldo_atual')[:10]

    context = {
        'total_clientes': Cliente.objects.count(),
        'clientes_ativos': Cliente.objects.filter(status='ATIVO').count(),
        'clientes_inativos': Cliente.objects.filter(status='INATIVO').count(),
        'total_faturas': Fatura.objects.count(),
        'faturas_pendentes': Fatura.objects.filter(status='PENDENTE').count(),
        'faturas_pagas': Fatura.objects.filter(status='PAGO').count(),
        'total_recargas': Recarga.objects.filter(status='CONFIRMADO').count(),
        'valor_recargas': Recarga.objects.filter(status='CONFIRMADO').aggregate(Sum('valor'))['valor__sum'] or 0,
        'consumo_mes_atual': Fatura.objects.filter(data_emissao__month=timezone.now().month, data_emissao__year=timezone.now().year).aggregate(Sum('consumo_kwh'))['consumo_kwh__sum'] or 0,
        'total_divida_pendente': Fatura.objects.filter(status__in=['PENDENTE', 'VENCIDO']).aggregate(Sum('valor_total'))['valor_total__sum'] or 0,
        'ultimos_clientes': Cliente.objects.all()[:5],
        'ultimas_faturas': Fatura.objects.all()[:5],
        'contadores_saldo_baixo': contadores_saldo_baixo,
        'saldo_baixo_limite': SALDO_BAIXO_LIMITE,
        'total_saldo_baixo': contadores_saldo_baixo.count(),
    }
    return render(request, 'dashboard.html', context)
