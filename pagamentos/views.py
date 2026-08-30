from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils import timezone
from .models import Tarifa, Pagamento, Fatura, Recarga
from .forms import TarifaForm, PagamentoForm, FaturaSimplesForm, RecargaForm
from equipamentos.models import LeituraConsumo, Contador
from decimal import Decimal
from datetime import timedelta, date
from django.http import HttpResponse
from django.conf import settings
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from django.db.models import Sum, Count, Q, F
from django.db import transaction

@login_required
def gerar_faturas_automaticas(request):
    """
    Gera faturas automaticamente para todos os clientes que tiveram leituras
    no último mês e ainda não têm fatura para esse período.
    """
    # Apenas clientes pós-pagos recebem faturas; o consumo pré-pago é
    # liquidado directamente no saldo quando a leitura é registada.
    leituras_pendentes = LeituraConsumo.objects.filter(
        contador__cliente__tipo_cliente='POS_PAGO'
    ).select_related('contador__cliente')
    faturas_geradas = 0
    
    # Período de referência (mês anterior ou atual)
    hoje = timezone.now()
    periodo = hoje.strftime('%B/%Y')
    
    for leitura in leituras_pendentes:
        # Verifica se já existe fatura para este cliente, contador e período
        existe = Fatura.objects.filter(
            cliente=leitura.contador.cliente,
            contador=leitura.contador,
            periodo_referencia=periodo
        ).exists()
        
        if not existe and leitura.contador.cliente:
            cliente = leitura.contador.cliente
            preco_kwh = Decimal('50.00')
            taxa_adicional = Decimal('0.00')
            
            if cliente.tarifa:
                preco_kwh = cliente.tarifa.preco_kwh
                if cliente.tipo_cliente == 'POS_PAGO':
                    taxa_adicional = cliente.tarifa.preco_cliente_pos
                else:
                    taxa_adicional = cliente.tarifa.preco_cliente_pre
            
            # Criar fatura
            valor_consumo = leitura.consumo * preco_kwh
            Fatura.objects.create(
                cliente=cliente,
                contador=leitura.contador,
                periodo_referencia=periodo,
                leitura_anterior=leitura.leitura_anterior,
                leitura_atual=leitura.leitura_atual,
                consumo_kwh=leitura.consumo,
                valor_consumo=valor_consumo,
                outras_taxas=taxa_adicional,
                valor_total=valor_consumo + taxa_adicional,
                status='PENDENTE',
                data_emissao=hoje.date(),
                data_vencimento=(hoje + timedelta(days=15)).date()
            )
            faturas_geradas += 1
    
    if faturas_geradas > 0:
        messages.success(request, f"Foram geradas {faturas_geradas} faturas com sucesso!")
    else:
        messages.info(request, "Nenhuma nova fatura precisou ser gerada.")
            
    return render(request, 'pagamentos/fatura_gerada_status.html', {
        'total': faturas_geradas,
        'periodo': periodo
    })

@login_required
def fatura_pdf(request, pk):
    fatura = get_object_or_404(Fatura, pk=pk)
    
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="fatura_{fatura.numero_fatura}.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Add logo at the top right
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo_iscat.png')
    try:
        if os.path.exists(logo_path):
            p.drawImage(logo_path, width - 180, height - 90, width=140, height=70, preserveAspectRatio=True)
    except Exception as e:
        print(f"Erro ao adicionar logo: {e}")

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, height - 50, "SISTEMA DE GESTÃO DE ENERGIA")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 70, f"Fatura: {fatura.numero_fatura}")
    p.drawString(50, height - 85, f"Data: {fatura.data_emissao.strftime('%d/%m/%Y')}")

    # Cliente
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, height - 120, "CLIENTE:")
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 135, f"Nome: {fatura.cliente.nome}")
    p.drawString(50, height - 150, f"NIF: {fatura.cliente.nif}")
    p.drawString(50, height - 165, f"Endereço: {fatura.cliente.morada or 'N/A'}")
    if fatura.contador:
        p.drawString(50, height - 180, f"Contador: {fatura.contador.numero_serie}")
    p.drawString(50, height - 195, f"Consumo do Mês: {fatura.consumo_kwh} kWh")
    p.drawString(50, height - 210, f"Valor do Consumo: {fatura.valor_consumo} Kz")
    p.drawString(50, height - 225, f"Estado: {fatura.get_status_display()}")

    # Detalhes
    y_offset = 240
    p.line(50, height - y_offset, 550, height - y_offset)
    p.drawString(50, height - y_offset - 20, "Descrição")
    p.drawRightString(540, height - y_offset - 20, "Valor (Kz)")
    p.line(50, height - y_offset - 30, 550, height - y_offset - 30)

    y_desc = height - y_offset - 50
    p.drawString(50, y_desc, f"Consumo de Energia ({fatura.consumo_kwh} kWh)")
    p.drawRightString(540, y_desc, f"{fatura.valor_consumo:,.2f} Kz")

    y = y_offset + 50
    if fatura.outras_taxas > 0:
        p.drawString(50, height - y, "Taxas Adicionais")
        p.drawRightString(540, height - y, f"{fatura.outras_taxas:,.2f} Kz")
        y += 20

    p.line(50, height - y, 550, height - y)
    y += 20
    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, height - y, "TOTAL A PAGAR")
    p.drawRightString(540, height - y, f"{fatura.valor_total} Kz")

    # Footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawCentredString(width / 2.0, 50, "Obrigado por utilizar nossos serviços.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response

@login_required
def fatura_detail(request, pk):
    fatura = get_object_or_404(Fatura, pk=pk)
    pagamentos = fatura.pagamentos.all()
    return render(request, 'pagamentos/fatura_detail.html', {'fatura': fatura, 'pagamentos': pagamentos})

@login_required
@csrf_protect
def registrar_pagamento(request, pk):
    from datetime import date as _date
    fatura = get_object_or_404(Fatura, pk=pk)

    hoje = _date.today()
    dias_atraso = max((hoje - fatura.data_vencimento).days, 0) if fatura.status != 'PAGO' else 0
    TAXA_DIARIA   = Decimal('0.02')
    TAXA_MAX      = Decimal('0.20')
    multa_calculada = Decimal('0.00')
    if dias_atraso > 0:
        taxa = min(TAXA_DIARIA * dias_atraso, TAXA_MAX)
        multa_calculada = (fatura.valor_consumo + fatura.outras_taxas) * taxa
    valor_com_multa = fatura.valor_consumo + fatura.outras_taxas + multa_calculada

    if request.method == 'POST':
        form = PagamentoForm(request.POST)
        if form.is_valid():
            pagamento = form.save(commit=False)
            pagamento.fatura = fatura
            if dias_atraso > 0 and multa_calculada > 0:
                fatura.multa_atraso = multa_calculada
                fatura.valor_total  = valor_com_multa
                fatura.save(update_fields=['multa_atraso', 'valor_total'])
            pagamento.save()
            messages.success(request, f"Pagamento de {pagamento.valor_pago:,.2f} Kz registado com sucesso!")
            return redirect('fatura_detail', pk=fatura.pk)
        else:
            messages.error(request, "Erro ao registar pagamento. Verifique os dados inseridos.")
    else:
        form = PagamentoForm(initial={'valor_pago': valor_com_multa})

    return render(request, 'pagamentos/registrar_pagamento.html', {
        'fatura':          fatura,
        'form':            form,
        'dias_atraso':     dias_atraso,
        'multa_calculada': multa_calculada,
        'valor_com_multa': valor_com_multa,
    })

@login_required
def fatura_list(request):
    if hasattr(request.user, 'perfil') and request.user.perfil.tipo_usuario == 'CLIENTE':
        faturas = Fatura.objects.filter(cliente__email=request.user.email) # Filtro simples por email para exemplo
    else:
        faturas = Fatura.objects.all()
    return render(request, 'pagamentos/fatura_list.html', {'faturas': faturas})


@login_required
def recarga_list(request):
    if hasattr(request.user, 'perfil') and request.user.perfil.tipo_usuario == 'CLIENTE':
        recargas = Recarga.objects.filter(cliente__email=request.user.email)
    else:
        recargas = Recarga.objects.select_related('cliente').all()

    total_confirmado = recargas.filter(status='CONFIRMADO').aggregate(
        total=Sum('valor')
    )['total'] or Decimal('0.00')
    return render(request, 'pagamentos/recarga_list.html', {
        'recargas': recargas,
        'total_confirmado': total_confirmado,
    })


@login_required
@csrf_protect
def recarga_create(request):
    if hasattr(request.user, 'perfil') and request.user.perfil.tipo_usuario == 'CLIENTE':
        messages.error(request, 'O registo de recargas é reservado aos operadores.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = RecargaForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                recarga = form.save(commit=False)
                recarga.status = 'CONFIRMADO'
                recarga.data_confirmacao = timezone.now()
                recarga.save()

                cliente = recarga.cliente
                cliente.saldo_atual = F('saldo_atual') + recarga.valor
                cliente.save(update_fields=['saldo_atual'])
                cliente.refresh_from_db(fields=['saldo_atual'])

            messages.success(
                request,
                f"Recarga de {recarga.valor:,.2f} Kz confirmada. "
                f"Saldo disponível de {cliente.saldo_atual:,.2f} Kz."
            )
            return redirect('recarga_list')
        messages.error(request, 'Não foi possível registar a recarga. Verifique os dados.')
    else:
        form = RecargaForm()
    return render(request, 'pagamentos/recarga_form.html', {'form': form})

@login_required
def fatura_create(request):
    import json as _json
    from clientes.models import Cliente as _Cliente

    if request.method == 'POST':
        form = FaturaSimplesForm(request.POST)
        if form.is_valid():
            fatura = form.save(commit=False)

            preco_kwh = Decimal('50.00')
            taxa_adicional = Decimal('0.00')

            if fatura.cliente.tarifa:
                preco_kwh = fatura.cliente.tarifa.preco_kwh
                if fatura.cliente.tipo_cliente == 'POS_PAGO':
                    taxa_adicional = fatura.cliente.tarifa.preco_cliente_pos
                else:
                    taxa_adicional = fatura.cliente.tarifa.preco_cliente_pre

            consumo = fatura.leitura_atual - fatura.leitura_anterior

            if consumo < 0:
                messages.error(request, "A leitura actual não pode ser inferior à anterior.")
                tarifas_json = _build_tarifas_json(_Cliente)
                return render(request, 'pagamentos/fatura_form.html', {'form': form, 'tarifas_json': tarifas_json})

            fatura.consumo_kwh = consumo
            fatura.valor_consumo = consumo * preco_kwh
            fatura.outras_taxas = taxa_adicional
            fatura.valor_total = fatura.valor_consumo + taxa_adicional

            fatura.save()
            messages.success(request, f"Fatura criada com sucesso! Total a pagar: {fatura.valor_total:,.2f} Kz")
            return redirect('fatura_list')
        else:
            messages.error(request, "Erro ao criar fatura. Verifique os campos.")
    else:
        form = FaturaSimplesForm()

    tarifas_json = _build_tarifas_json(_Cliente)
    return render(request, 'pagamentos/fatura_form.html', {'form': form, 'tarifas_json': tarifas_json})


def _build_tarifas_json(Cliente):
    import json as _json
    from decimal import Decimal as _D
    data = {}
    for c in Cliente.objects.select_related('tarifa').filter(tipo_cliente='POS_PAGO'):
        if c.tarifa:
            preco = float(c.tarifa.preco_kwh)
            taxa  = float(c.tarifa.preco_cliente_pos)
        else:
            preco = 50.0
            taxa  = 0.0
        data[str(c.pk)] = {'preco_kwh': preco, 'taxa': taxa}
    return _json.dumps(data)

@login_required
def tarifa_list(request):
    tarifas = Tarifa.objects.all()
    return render(request, 'pagamentos/tarifa_list.html', {'tarifas': tarifas})

@login_required
def tarifa_create(request):
    if request.method == 'POST':
        form = TarifaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tarifa_list')
    else:
        form = TarifaForm()
    return render(request, 'pagamentos/tarifa_form.html', {'form': form})

@login_required
def tarifa_update(request, pk):
    tarifa = get_object_or_404(Tarifa, pk=pk)
    if request.method == 'POST':
        form = TarifaForm(request.POST, instance=tarifa)
        if form.is_valid():
            form.save()
            return redirect('tarifa_list')
    else:
        form = TarifaForm(instance=tarifa)
    return render(request, 'pagamentos/tarifa_form.html', {'form': form})

@login_required
def suspender_contador(request, pk):
    """Suspende o contador por dívida"""
    contador = get_object_or_404(Contador, pk=pk)
    contador.status = 'SUSPENSO'
    contador.data_suspensao = timezone.now()
    contador.save()
    return redirect('controlo_divida')

@login_required
def reativar_contador(request, pk):
    """Reativa o contador quando a dívida for paga"""
    contador = get_object_or_404(Contador, pk=pk)
    contador.status = 'ATIVO'
    contador.data_suspensao = None
    contador.save()
    return redirect('controlo_divida')

@login_required
def acionar_suspensao_automatica(request):
    """Aciona manualmente o comando de suspensão automática"""
    from django.core.management import call_command
    
    try:
        call_command('suspender_devedores')
        messages.success(request, "Processo de suspensão automática executado com sucesso.")
    except Exception as e:
        messages.error(request, f"Erro ao executar suspensão: {str(e)}")
        
    return redirect('controlo_divida')

@login_required
def fatura_delete(request, pk):
    fatura = get_object_or_404(Fatura, pk=pk)
    if request.method == 'POST':
        numero = fatura.numero_fatura
        fatura.delete()
        messages.success(request, f"Fatura '{numero}' eliminada com sucesso.")
        return redirect('fatura_list')
    return redirect('fatura_list')

@login_required
def controlo_divida(request):
    """
    Dashboard de controle de dívidas - mostra clientes com faturas pendentes/vencidas
    """
    hoje = date.today()
    
    # Faturas não pagas
    faturas_pendentes = Fatura.objects.filter(
        status__in=['PENDENTE', 'VENCIDO']
    ).select_related('cliente').order_by('-data_vencimento')
    
    # Separar faturas vencidas
    faturas_vencidas = [f for f in faturas_pendentes if f.data_vencimento < hoje]
    
    # Agrupar por cliente para calcular dívida total
    clientes_divida = {}
    total_divida = Decimal('0.00')
    
    for fatura in faturas_pendentes:
        cliente = fatura.cliente
        if cliente not in clientes_divida:
            clientes_divida[cliente] = {
                'total_divida': Decimal('0.00'),
                'faturas_vencidas': 0,
                'faturas_pendentes': 0,
                'dias_vencimento': 0,
                'faturas': []
            }
        
        clientes_divida[cliente]['total_divida'] += fatura.valor_total
        clientes_divida[cliente]['faturas'].append(fatura)
        total_divida += fatura.valor_total
        
        if fatura.data_vencimento < hoje:
            clientes_divida[cliente]['faturas_vencidas'] += 1
            dias = (hoje - fatura.data_vencimento).days
            if dias > clientes_divida[cliente]['dias_vencimento']:
                clientes_divida[cliente]['dias_vencimento'] = dias
        else:
            clientes_divida[cliente]['faturas_pendentes'] += 1
    
    # Ordenar por valor de dívida (maior para menor)
    clientes_divida_ordenados = sorted(
        clientes_divida.items(),
        key=lambda x: x[1]['total_divida'],
        reverse=True
    )
    
    # Contar contadores suspensos
    contadores_suspensos = Contador.objects.filter(status='SUSPENSO').count()
    
    context = {
        'clientes_divida': clientes_divida_ordenados,
        'faturas_vencidas': faturas_vencidas,
        'total_divida': total_divida,
        'total_clientes_devendo': len(clientes_divida),
        'total_faturas_pendentes': faturas_pendentes.count(),
        'contadores_suspensos': contadores_suspensos,
    }
    
    return render(request, 'pagamentos/controlo_divida.html', context)
