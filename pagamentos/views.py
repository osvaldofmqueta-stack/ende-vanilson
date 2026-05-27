from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.utils import timezone
from .models import Tarifa, Pagamento, Fatura
from .forms import TarifaForm, PagamentoForm, FaturaSimplesForm
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

@login_required
def gerar_faturas_automaticas(request):
    """
    Gera faturas automaticamente para todos os clientes que tiveram leituras
    no último mês e ainda não têm fatura para esse período.
    """
    leituras_pendentes = LeituraConsumo.objects.all() # Simplificado para demonstração
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
    p.drawRightString(540, y_desc, f"{fatura.valor_consumo}")

    y = y_offset + 50
    if fatura.outras_taxas > 0:
        p.drawString(50, height - y, "Taxas Adicionais")
        p.drawRightString(540, height - y, f"{fatura.outras_taxas}")
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
    fatura = get_object_or_404(Fatura, pk=pk)
    
    if request.method == 'POST':
        form = PagamentoForm(request.POST)
        if form.is_valid():
            pagamento = form.save(commit=False)
            pagamento.fatura = fatura
            pagamento.save()
            messages.success(request, f"Pagamento de {pagamento.valor_pago} Kz registrado com sucesso!")
            return redirect('fatura_detail', pk=fatura.pk)
        else:
            messages.error(request, "Erro ao registrar pagamento. Verifique os dados inseridos.")
    else:
        form = PagamentoForm(initial={'valor_pago': fatura.valor_total})
    
    return render(request, 'pagamentos/registrar_pagamento.html', {
        'fatura': fatura, 
        'form': form
    })

@login_required
def fatura_list(request):
    if hasattr(request.user, 'perfil') and request.user.perfil.tipo_usuario == 'CLIENTE':
        faturas = Fatura.objects.filter(cliente__email=request.user.email) # Filtro simples por email para exemplo
    else:
        faturas = Fatura.objects.all()
    return render(request, 'pagamentos/fatura_list.html', {'faturas': faturas})

@login_required
def fatura_create(request):
    if request.method == 'POST':
        form = FaturaSimplesForm(request.POST)
        if form.is_valid():
            fatura = form.save(commit=False)
            
            # Lógica simples de cálculo baseada na tarifa do cliente
            # Se o cliente não tiver tarifa, usamos um valor padrão
            preco_kwh = Decimal('50.00') # Padrão
            taxa_adicional = Decimal('0.00')
            
            if fatura.cliente.tarifa:
                preco_kwh = fatura.cliente.tarifa.preco_kwh
                if fatura.cliente.tipo_cliente == 'POS_PAGO':
                    taxa_adicional = fatura.cliente.tarifa.preco_cliente_pos
                else:
                    taxa_adicional = fatura.cliente.tarifa.preco_cliente_pre
            
            consumo = fatura.leitura_atual - fatura.leitura_anterior
            
            if consumo < 0:
                messages.error(request, "A leitura atual não pode ser inferior à anterior.")
                return render(request, 'pagamentos/fatura_form.html', {'form': form})

            fatura.consumo_kwh = consumo
            fatura.valor_consumo = consumo * preco_kwh
            fatura.outras_taxas = taxa_adicional
            fatura.valor_total = fatura.valor_consumo + taxa_adicional
            
            fatura.save()
            messages.success(request, "Fatura manual criada com sucesso!")
            return redirect('fatura_list')
        else:
            messages.error(request, "Erro ao criar fatura. Verifique os campos.")
    else:
        form = FaturaSimplesForm()
    return render(request, 'pagamentos/fatura_form.html', {'form': form})

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
