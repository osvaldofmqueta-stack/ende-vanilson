from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from django.contrib import messages
from decimal import Decimal, InvalidOperation
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
def contador_delete(request, pk):
    from django.contrib import messages
    contador = get_object_or_404(Contador, pk=pk)
    if request.method == 'POST':
        numero = contador.numero_serie
        contador.delete()
        messages.success(request, f"Contador '{numero}' eliminado com sucesso.")
        return redirect('contador_list')
    return redirect('contador_list')

@login_required
def contador_marcar_avariado(request, pk):
    contador = get_object_or_404(Contador, pk=pk)
    contador.status = 'AVARIADO'
    contador.save()
    from django.contrib import messages
    messages.warning(request, f"Contador {contador.numero_serie} marcado como avariado.")
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
            leitura_anterior = contador.leitura_atual
            try:
                leitura_atual_dec = Decimal(nova_leitura)
            except InvalidOperation:
                messages.error(request, 'Informe uma leitura numérica válida.')
                return render(request, 'equipamentos/contador_leitura.html', {'contador': contador})

            if leitura_atual_dec < leitura_anterior:
                messages.error(request, 'A leitura atual não pode ser inferior à leitura anterior.')
                return render(request, 'equipamentos/contador_leitura.html', {'contador': contador})
            
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
            
            consumo = leitura_atual_dec - leitura_anterior
            if consumo > 0 and contador.cliente and contador.cliente.tipo_cliente == 'PRE_PAGO':
                cliente = contador.cliente
                tarifa = cliente.tarifa
                preco_kwh = tarifa.preco_kwh if tarifa else Decimal('50.00')
                custo_consumo = consumo * preco_kwh

                if cliente.saldo_atual >= custo_consumo:
                    cliente.saldo_atual -= custo_consumo
                    cliente.save()
                    messages.success(request, f"Leitura registada. Consumo: {consumo} kWh ({custo_consumo:.2f} Kz debitados). Saldo restante: {cliente.saldo_atual:.2f} Kz.")
                else:
                    messages.warning(request, f"Leitura registada mas saldo insuficiente. Consumo: {consumo} kWh ({custo_consumo:.2f} Kz). Saldo actual: {cliente.saldo_atual:.2f} Kz.")
            elif consumo > 0 and contador.cliente:
                messages.success(
                    request,
                    f"Leitura registada. Consumo: {consumo} kWh. "
                    "O valor será incluído na fatura do cliente pós-pago."
                )

            return redirect('contador_historico', pk=pk)
            
    return render(request, 'equipamentos/contador_leitura.html', {'contador': contador})
