from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Contador
from .forms import ContadorForm

@login_required
def contador_list(request):
    search_query = request.GET.get('search', '')
    if hasattr(request.user, 'perfil') and request.user.perfil.tipo_usuario == 'CLIENTE':
        contadores = Contador.objects.filter(cliente__email=request.user.email)
    else:
        if search_query:
            contadores = Contador.objects.filter(models.Q(numero_serie__icontains=search_query))
        else:
            contadores = Contador.objects.all()
    return render(request, 'equipamentos/contador_list.html', {'contadores': contadores, 'search_query': search_query})

@login_required
def contador_create(request):
    if request.method == 'POST':
        form = ContadorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contador_list')
    else:
        form = ContadorForm()
    return render(request, 'equipamentos/contador_form.html', {'form': form, 'title': 'Registrar Contador'})

@login_required
def contador_update(request, pk):
    contador = get_object_or_404(Contador, pk=pk)
    if request.method == 'POST':
        form = ContadorForm(request.POST, instance=contador)
        if form.is_valid():
            form.save()
            return redirect('contador_list')
    else:
        form = ContadorForm(instance=contador)
    return render(request, 'equipamentos/contador_form.html', {'form': form, 'title': 'Editar Contador'})

@login_required
def contador_toggle_status(request, pk):
    contador = get_object_or_404(Contador, pk=pk)
    if contador.status == 'ATIVO':
        contador.status = 'INATIVO'
    else:
        contador.status = 'ATIVO'
    contador.save()
    return redirect('contador_list')

@login_required
def contador_marcar_avariado(request, pk):
    contador = get_object_or_404(Contador, pk=pk)
    contador.status = 'AVARIADO'
    contador.save()
    
    # Se o cliente for pré-pago, passa para pós-pago (sem contador funcional)
    if contador.cliente and contador.cliente.tipo_cliente == 'PRE_PAGO':
        cliente = contador.cliente
        cliente.tipo_cliente = 'POS_PAGO'
        cliente.save()
        
    return redirect('contador_list')

from django.utils import timezone

@login_required
def contador_historico(request, pk):
    contador = get_object_or_404(Contador, pk=pk)
    historico = contador.historico_manutencao.all()
    leituras = contador.leituras.all().order_by('-data_leitura')
    from pagamentos.models import Fatura, Recarga
    faturas = Fatura.objects.filter(contador=contador).order_by('-data_emissao')
    recargas = Recarga.objects.filter(cliente=contador.cliente).order_by('-data_recarga')
    
    context = {
        'contador': contador,
        'historico': historico,
        'leituras': leituras,
        'faturas': faturas,
        'recargas': recargas,
    }
    return render(request, 'equipamentos/contador_historico.html', context)

@login_required
def contador_registrar_leitura(request, pk):
    contador = get_object_or_404(Contador, pk=pk)
    if request.method == 'POST':
        nova_leitura = request.POST.get('leitura_atual')
        if nova_leitura:
            from decimal import Decimal
            leitura_anterior = contador.leitura_atual
            leitura_atual_dec = Decimal(nova_leitura)
            
            # Atualiza o contador
            contador.leitura_atual = leitura_atual_dec
            contador.data_ultima_leitura = timezone.now()
            contador.save()
            
            # Registrar no histórico de consumo
            from .models import LeituraConsumo
            LeituraConsumo.objects.create(
                contador=contador,
                leitura_anterior=leitura_anterior,
                leitura_atual=leitura_atual_dec,
                consumo=leitura_atual_dec - leitura_anterior,
                operador=request.user
            )
            
            # Se for POS_PAGO, gera fatura
            if contador.tipo_contador == 'POS_PAGO':
                from pagamentos.models import Fatura
                import datetime
                
                consumo = leitura_atual_dec - leitura_anterior
                if consumo > 0:
                    tarifa = contador.cliente.tarifa
                    preco_kwh = tarifa.preco_kwh if tarifa else Decimal('50.00')
                    taxa_fixa = tarifa.taxa_fixa if tarifa else Decimal('0.00')
                    
                    valor_consumo = consumo * preco_kwh
                    valor_total = valor_consumo + taxa_fixa
                    
                    Fatura.objects.create(
                        cliente=contador.cliente,
                        contador=contador,
                        periodo_referencia=timezone.now().strftime('%B/%Y'),
                        leitura_anterior=leitura_anterior,
                        leitura_atual=leitura_atual_dec,
                        consumo_kwh=consumo,
                        valor_consumo=valor_consumo,
                        outras_taxas=taxa_fixa,
                        valor_total=valor_total,
                        data_emissao=datetime.date.today(),
                        data_vencimento=datetime.date.today() + datetime.timedelta(days=15)
                    )
            
            return redirect('contador_historico', pk=pk)
            
    return render(request, 'equipamentos/contador_leitura.html', {'contador': contador})
