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
        cliente__tipo_cliente='PRE_PAGO',
        cliente__saldo_atual__lte=SALDO_BAIXO_LIMITE
    ).select_related('cliente').order_by('cliente__saldo_atual')[:10]

    clientes_pre_pago = Cliente.objects.filter(tipo_cliente='PRE_PAGO')
    clientes_pos_pago = Cliente.objects.filter(tipo_cliente='POS_PAGO')
    contadores = Contador.objects.select_related('cliente')
    faturas_pos_pago = Fatura.objects.filter(cliente__tipo_cliente='POS_PAGO')

    context = {
        'total_clientes': Cliente.objects.count(),
        'clientes_ativos': Cliente.objects.filter(status='ATIVO').count(),
        'clientes_inativos': Cliente.objects.filter(status='INATIVO').count(),
        'clientes_pre_pago': clientes_pre_pago.count(),
        'clientes_pos_pago': clientes_pos_pago.count(),
        'saldo_pre_pago_total': clientes_pre_pago.aggregate(Sum('saldo_atual'))['saldo_atual__sum'] or Decimal('0.00'),
        'total_contadores': contadores.count(),
        'contadores_ativos': contadores.filter(status='ATIVO').count(),
        'contadores_pre_pago': contadores.filter(cliente__tipo_cliente='PRE_PAGO').count(),
        'contadores_pos_pago': contadores.filter(cliente__tipo_cliente='POS_PAGO').count(),
        'total_faturas': Fatura.objects.count(),
        'faturas_pendentes': faturas_pos_pago.filter(status__in=['PENDENTE', 'VENCIDO']).count(),
        'faturas_pagas': faturas_pos_pago.filter(status='PAGO').count(),
        'valor_faturas_pendentes': faturas_pos_pago.filter(
            status__in=['PENDENTE', 'VENCIDO']
        ).aggregate(Sum('valor_total'))['valor_total__sum'] or Decimal('0.00'),
        'total_recargas': Recarga.objects.filter(status='CONFIRMADO').count(),
        'valor_recargas': Recarga.objects.filter(status='CONFIRMADO').aggregate(Sum('valor'))['valor__sum'] or 0,
        'recargas_hoje': Recarga.objects.filter(
            status='CONFIRMADO',
            data_recarga__date=timezone.now().date()
        ).count(),
        'consumo_mes_atual': faturas_pos_pago.filter(
            data_emissao__month=timezone.now().month,
            data_emissao__year=timezone.now().year
        ).aggregate(Sum('consumo_kwh'))['consumo_kwh__sum'] or 0,
        'total_divida_pendente': faturas_pos_pago.filter(
            status__in=['PENDENTE', 'VENCIDO']
        ).aggregate(Sum('valor_total'))['valor_total__sum'] or 0,
        'ultimos_clientes': Cliente.objects.all()[:5],
        'ultimas_faturas': faturas_pos_pago.select_related('cliente')[:5],
        'contadores_saldo_baixo': contadores_saldo_baixo,
        'saldo_baixo_limite': SALDO_BAIXO_LIMITE,
        'total_saldo_baixo': contadores_saldo_baixo.count(),
    }
    return render(request, 'dashboard.html', context)
