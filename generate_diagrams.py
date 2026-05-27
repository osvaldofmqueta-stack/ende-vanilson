"""
Gera os 4 diagramas UML do Sistema de Gestão de Energia:
  1. Diagrama de Entidade-Relacionamento (DER)
  2. Diagrama de Classes (UML)
  3. Diagrama de Relacionamento entre Módulos
  4. Diagrama de Casos de Uso
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe

os.makedirs('static/diagrams', exist_ok=True)

# ── Palette ────────────────────────────────────────────────────────────────
C_BLUE_DARK  = '#1a3a5c'
C_BLUE_MED   = '#2d6a9f'
C_BLUE_LIGHT = '#e8f0f7'
C_GREEN      = '#1e8449'
C_GREEN_L    = '#d5f5e3'
C_ORANGE     = '#d35400'
C_ORANGE_L   = '#fde8d8'
C_PURPLE     = '#6c3483'
C_PURPLE_L   = '#e8daef'
C_RED        = '#c0392b'
C_RED_L      = '#fdedec'
C_GRAY       = '#5d6d7e'
C_GRAY_L     = '#f2f3f4'
C_WHITE      = '#ffffff'
C_LINE       = '#aab7c4'


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def draw_entity(ax, x, y, w, h, title, attrs, header_color=C_BLUE_DARK, body_color=C_BLUE_LIGHT):
    """Draws a UML/ER entity box with header + attribute rows."""
    row_h = 0.38
    total_h = 0.55 + len(attrs) * row_h

    # Shadow
    ax.add_patch(FancyBboxPatch((x + 0.04, y - total_h - 0.04), w, total_h,
                                boxstyle="round,pad=0.05", linewidth=0,
                                facecolor='#cccccc', zorder=1))
    # Header
    ax.add_patch(FancyBboxPatch((x, y - 0.55), w, 0.55,
                                boxstyle="round,pad=0.03", linewidth=1.2,
                                edgecolor=C_BLUE_MED, facecolor=header_color, zorder=2))
    ax.text(x + w / 2, y - 0.27, title,
            ha='center', va='center', fontsize=9.5, fontweight='bold',
            color=C_WHITE, zorder=3)

    # Body
    ax.add_patch(FancyBboxPatch((x, y - total_h), w, total_h - 0.55,
                                boxstyle="round,pad=0.03", linewidth=1.2,
                                edgecolor=C_BLUE_MED, facecolor=body_color, zorder=2))

    for i, attr in enumerate(attrs):
        ay = y - 0.55 - (i + 0.5) * row_h
        # PK / FK decoration
        icon = ''
        color = '#2c3e50'
        if attr.startswith('PK '):
            icon = '[PK] '
            attr = attr[3:]
            color = C_ORANGE
        elif attr.startswith('FK '):
            icon = '[FK] '
            attr = attr[3:]
            color = C_BLUE_MED
        ax.text(x + 0.12, ay, f"{icon}{attr}", ha='left', va='center',
                fontsize=7.5, color=color, zorder=3)
        if i < len(attrs) - 1:
            ax.plot([x + 0.05, x + w - 0.05], [ay - row_h / 2, ay - row_h / 2],
                    color=C_LINE, linewidth=0.4, zorder=3)

    # Returns top-center and bottom-center for connections
    cx = x + w / 2
    return dict(top=(cx, y), bottom=(cx, y - total_h),
                left=(x, y - total_h / 2), right=(x + w, y - total_h / 2))


def arrow(ax, p1, p2, label='', card_start='', card_end='', color=C_BLUE_MED, style='-'):
    """Draw a connecting arrow with optional cardinality labels."""
    ax.annotate('', xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle='->', color=color, lw=1.3,
                                connectionstyle='arc3,rad=0.0'), zorder=4)
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    if label:
        ax.text(mx, my + 0.12, label, ha='center', va='bottom',
                fontsize=6.5, color=C_GRAY,
                bbox=dict(boxstyle='round,pad=0.2', fc=C_WHITE, ec=C_LINE, lw=0.5))
    if card_start:
        ax.text(p1[0] + (p2[0] - p1[0]) * 0.08,
                p1[1] + (p2[1] - p1[1]) * 0.08 + 0.08,
                card_start, ha='center', va='center', fontsize=7, color=C_RED,
                fontweight='bold')
    if card_end:
        ax.text(p2[0] - (p2[0] - p1[0]) * 0.08,
                p2[1] - (p2[1] - p1[1]) * 0.08 + 0.08,
                card_end, ha='center', va='center', fontsize=7, color=C_RED,
                fontweight='bold')


# ═══════════════════════════════════════════════════════════════════════════
# 1. DIAGRAMA DE ENTIDADE-RELACIONAMENTO
# ═══════════════════════════════════════════════════════════════════════════

def draw_er():
    fig, ax = plt.subplots(figsize=(24, 18))
    ax.set_xlim(0, 24)
    ax.set_ylim(-17, 1.5)
    ax.axis('off')
    fig.patch.set_facecolor('#f7f9fc')
    ax.set_facecolor('#f7f9fc')

    # Title
    ax.text(12, 1.1, 'Diagrama de Entidade-Relacionamento',
            ha='center', va='center', fontsize=18, fontweight='bold', color=C_BLUE_DARK)
    ax.text(12, 0.5, 'Sistema de Gestão de Energia',
            ha='center', va='center', fontsize=11, color=C_GRAY)

    EW = 3.8  # entity width

    # ── Row 1 ──────────────────────────────────────────────────────────────
    p_tarifa = draw_entity(ax, 0.5, 0, EW, 0, 'TARIFA',
        ['PK id', 'nome', 'preco_kwh (Kz)', 'preco_cliente_pre (Kz)', 'preco_cliente_pos (Kz)'],
        C_PURPLE)

    p_cliente = draw_entity(ax, 5.2, 0, EW, 0, 'CLIENTE',
        ['PK id', 'numero_cliente', 'nome', 'NIF', 'BI', 'morada', 'telefone', 'email',
         'tipo_cliente (PRE/POS)', 'status', 'saldo_atual (Kz)', 'FK tarifa_id'],
        C_BLUE_DARK)

    p_perfil = draw_entity(ax, 10.0, 0, EW, 0, 'PERFIL (Utilizador)',
        ['PK id', 'FK user_id', 'tipo_usuario', 'telefone'],
        C_PURPLE)

    p_contrato = draw_entity(ax, 14.8, 0, EW, 0, 'CONTRATO',
        ['PK id', 'codigo_contrato', 'FK cliente_id', 'data_inicio', 'data_fim',
         'tipo', 'status', 'observacoes'],
        C_GREEN)

    p_notif = draw_entity(ax, 19.6, 0, EW, 0, 'NOTIFICAÇÃO',
        ['PK id', 'FK cliente_id', 'tipo', 'mensagem', 'lida', 'data_criacao'],
        C_ORANGE)

    # ── Row 2 ──────────────────────────────────────────────────────────────
    p_contador = draw_entity(ax, 3.5, -7, EW, 0, 'CONTADOR',
        ['PK id', 'numero_serie', 'FK cliente_id', 'status', 'endereco_instalacao',
         'modelo', 'fabricante', 'data_instalacao'],
        C_BLUE_MED)

    p_fatura = draw_entity(ax, 8.3, -7, EW + 0.4, 0, 'FATURA',
        ['PK id', 'numero_fatura', 'FK cliente_id', 'FK contador_id',
         'periodo_referencia', 'leitura_anterior', 'leitura_atual',
         'consumo_kwh', 'valor_consumo (Kz)', 'multa_atraso (Kz)',
         'outras_taxas (Kz)', 'valor_total (Kz)', 'status', 'data_emissao', 'data_vencimento'],
        C_RED)

    p_recarga = draw_entity(ax, 13.5, -7, EW, 0, 'RECARGA',
        ['PK id', 'numero_recarga', 'FK cliente_id', 'valor (Kz)',
         'metodo_pagamento', 'status', 'data_recarga'],
        C_GREEN)

    p_relatorio = draw_entity(ax, 18.3, -7, EW + 0.3, 0, 'RELATÓRIO GERADO',
        ['PK id', 'titulo', 'tipo_relatorio', 'periodo_inicio',
         'periodo_fim', 'gerado_por', 'data_geracao', 'observacoes'],
        C_PURPLE)

    # ── Row 3 ──────────────────────────────────────────────────────────────
    p_hist = draw_entity(ax, 0.5, -13.5, EW, 0, 'HISTÓRICO MANUTENÇÃO',
        ['PK id', 'FK contador_id', 'tipo_manutencao', 'data_manutencao',
         'tecnico', 'descricao', 'custo (Kz)'],
        C_ORANGE)

    p_cartao = draw_entity(ax, 5.2, -13.5, EW, 0, 'CARTÃO RECARGA',
        ['PK id', 'FK contador_id', 'codigo_cartao', 'valor (Kz)',
         'status', 'data_criacao', 'data_uso'],
        C_ORANGE)

    p_pagamento = draw_entity(ax, 9.9, -13.5, EW, 0, 'PAGAMENTO',
        ['PK id', 'numero_pagamento', 'FK fatura_id', 'valor_pago (Kz)',
         'metodo_pagamento', 'referencia_multicaixa', 'data_pagamento'],
        C_RED)

    p_recibo = draw_entity(ax, 14.6, -13.5, EW, 0, 'RECIBO',
        ['PK id', 'numero_recibo', 'FK cliente_id', 'FK fatura_id',
         'FK recarga_id', 'valor (Kz)', 'metodo_pagamento', 'data_emissao'],
        C_GREEN)

    # ── Relationships (arrows) ────────────────────────────────────────────
    # Tarifa → Cliente
    arrow(ax, p_tarifa['right'], p_cliente['left'], '1 : N', '1', 'N')
    # Cliente → Contrato
    arrow(ax, p_cliente['right'], p_contrato['left'], '1 : N', '1', 'N')
    # Cliente → Notificação
    arrow(ax, p_cliente['right'], (p_notif['left'][0], p_notif['left'][1]),
          '1 : N', '1', 'N')
    # Cliente → Contador
    arrow(ax, p_cliente['bottom'], p_contador['top'], '1 : N\n(Pré-pago)', '1', 'N')
    # Cliente → Fatura
    arrow(ax, (p_cliente['bottom'][0], p_cliente['bottom'][1]),
          (p_fatura['top'][0], p_fatura['top'][1]), '1 : N\n(Pós-pago)', '1', 'N')
    # Cliente → Recarga
    arrow(ax, (p_cliente['bottom'][0] + 0.2, p_cliente['bottom'][1]),
          p_recarga['top'], '1 : N', '1', 'N')
    # Contador → Fatura
    arrow(ax, p_contador['right'], p_fatura['left'], '1 : N', '1', 'N')
    # Contador → HistóricoMan
    arrow(ax, p_contador['bottom'], p_hist['top'], '1 : N', '1', 'N')
    # Contador → CartãoRecarga
    arrow(ax, (p_contador['bottom'][0] + 0.3, p_contador['bottom'][1]),
          p_cartao['top'], '1 : N', '1', 'N')
    # Fatura → Pagamento
    arrow(ax, p_fatura['bottom'], p_pagamento['top'], '1 : N', '1', 'N')
    # Fatura → Recibo
    arrow(ax, (p_fatura['bottom'][0] + 0.4, p_fatura['bottom'][1]),
          p_recibo['top'], '1 : N', '1', 'N')
    # Recarga → Recibo
    arrow(ax, p_recarga['bottom'], (p_recibo['top'][0] - 0.2, p_recibo['top'][1]),
          '0 : N', '1', 'N')
    # Cliente → Recibo
    arrow(ax, (p_cliente['bottom'][0] + 0.5, p_cliente['bottom'][1] - 0.3),
          (p_recibo['top'][0] + 0.3, p_recibo['top'][1]), '1 : N', '1', 'N')

    # Legend
    leg_x, leg_y = 0.3, -16.0
    ax.add_patch(FancyBboxPatch((leg_x - 0.2, leg_y - 0.6), 23.4, 1.0,
                                boxstyle='round,pad=0.1', facecolor=C_WHITE,
                                edgecolor=C_LINE, lw=0.8))
    for i, (color, label) in enumerate([
        (C_BLUE_DARK, 'Módulo Clientes'),
        (C_GREEN, 'Módulo Contratos/Recargas'),
        (C_RED, 'Módulo Faturação'),
        (C_ORANGE, 'Módulo Equipamentos'),
        (C_PURPLE, 'Módulo Utilizadores/Relatórios'),
    ]):
        bx = leg_x + i * 4.6
        ax.add_patch(FancyBboxPatch((bx, leg_y - 0.3), 0.35, 0.35,
                                    boxstyle='round,pad=0.02', facecolor=color, edgecolor='none'))
        ax.text(bx + 0.5, leg_y - 0.12, label, fontsize=8, va='center', color=C_GRAY)

    plt.tight_layout(pad=0.5)
    fig.savefig('static/diagrams/1_diagrama_ER.png', dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("✓ 1_diagrama_ER.png")


# ═══════════════════════════════════════════════════════════════════════════
# 2. DIAGRAMA DE CLASSES (UML)
# ═══════════════════════════════════════════════════════════════════════════

def draw_class():
    fig, ax = plt.subplots(figsize=(26, 20))
    ax.set_xlim(0, 26)
    ax.set_ylim(-19, 1.5)
    ax.axis('off')
    fig.patch.set_facecolor('#f7f9fc')
    ax.set_facecolor('#f7f9fc')

    ax.text(13, 1.1, 'Diagrama de Classes (UML)',
            ha='center', va='center', fontsize=18, fontweight='bold', color=C_BLUE_DARK)
    ax.text(13, 0.5, 'Sistema de Gestão de Energia — Django Models',
            ha='center', va='center', fontsize=11, color=C_GRAY)

    def draw_class_box(x, y, name, attrs, methods, hcolor=C_BLUE_DARK):
        row_h = 0.34
        h_header = 0.55
        h_attrs = max(len(attrs), 1) * row_h + 0.15
        h_methods = max(len(methods), 1) * row_h + 0.15
        total = h_header + h_attrs + h_methods

        # Shadow
        ax.add_patch(FancyBboxPatch((x + 0.05, y - total - 0.05), 4.2, total,
                                    boxstyle='round,pad=0.04', linewidth=0,
                                    facecolor='#c0c0c0', zorder=1))
        # Header
        ax.add_patch(FancyBboxPatch((x, y - h_header), 4.2, h_header,
                                    boxstyle='round,pad=0.03', linewidth=1.3,
                                    edgecolor=C_BLUE_MED, facecolor=hcolor, zorder=2))
        ax.text(x + 2.1, y - h_header / 2, '«class»', ha='center', va='center',
                fontsize=6.5, color=(1, 1, 1, 0.65), style='italic', zorder=3)
        ax.text(x + 2.1, y - h_header * 0.65, name, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color=C_WHITE, zorder=3)

        # Attributes section
        ay_start = y - h_header
        ax.add_patch(FancyBboxPatch((x, ay_start - h_attrs), 4.2, h_attrs,
                                    boxstyle='round,pad=0.03', linewidth=1.2,
                                    edgecolor=C_BLUE_MED, facecolor='#fafcff', zorder=2))
        for i, a in enumerate(attrs):
            ay = ay_start - 0.1 - (i + 0.5) * row_h
            icon = '# ' if a.startswith('+ ') else '- '
            ax.text(x + 0.12, ay, a, ha='left', va='center',
                    fontsize=7, color='#1a3a5c', zorder=3, family='monospace')

        # Methods section
        my_start = ay_start - h_attrs
        ax.add_patch(FancyBboxPatch((x, my_start - h_methods), 4.2, h_methods,
                                    boxstyle='round,pad=0.03', linewidth=1.2,
                                    edgecolor=C_BLUE_MED, facecolor='#f0f7ff', zorder=2))
        ax.text(x + 0.08, my_start - 0.08, '  — Métodos —',
                ha='left', va='top', fontsize=6.5, color=C_BLUE_MED,
                style='italic', zorder=3)
        for i, m in enumerate(methods):
            my = my_start - 0.22 - (i + 0.5) * row_h
            ax.text(x + 0.12, my, m, ha='left', va='center',
                    fontsize=7, color=C_GREEN, zorder=3, family='monospace')

        cx = x + 2.1
        return dict(top=(cx, y), bottom=(cx, y - total),
                    left=(x, y - total / 2), right=(x + 4.2, y - total / 2),
                    total_h=total)

    def assoc(ax, p1, p2, label='', style='assoc', color=C_BLUE_MED):
        arrowstyle = '->' if style == 'assoc' else '-|>'
        ax.annotate('', xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle=arrowstyle, color=color, lw=1.3,
                                    connectionstyle='arc3,rad=0.05'), zorder=5)
        if label:
            mx = (p1[0] + p2[0]) / 2
            my = (p1[1] + p2[1]) / 2 + 0.12
            ax.text(mx, my, label, ha='center', va='bottom', fontsize=6.5, color=C_GRAY,
                    bbox=dict(boxstyle='round,pad=0.18', fc=C_WHITE, ec=C_LINE, lw=0.5),
                    zorder=6)

    # Column 1
    p_user = draw_class_box(0.3, 0, 'User (Django)', [
        '+ id: int',
        '+ username: str',
        '+ password: str',
        '+ email: str',
        '+ is_staff: bool',
        '+ is_superuser: bool',
    ], ['+ authenticate()', '+ has_perm()'], C_PURPLE)

    p_perfil = draw_class_box(0.3, -7.5, 'Perfil', [
        '+ id: int',
        '+ user: User',
        '+ tipo_usuario: str',
        '+ telefone: str',
    ], ['+ get_tipo_usuario_display()', '+ __str__()'], C_PURPLE)

    # Column 2
    p_tarifa = draw_class_box(5.5, 0, 'Tarifa', [
        '+ id: int',
        '+ nome: str',
        '+ preco_kwh: Decimal',
        '+ preco_cliente_pre: Decimal',
        '+ preco_cliente_pos: Decimal',
    ], ['+ __str__()', '+ calcular_valor(kwh)'], C_GREEN)

    p_cliente = draw_class_box(5.5, -7.5, 'Cliente', [
        '+ id: int',
        '+ numero_cliente: str',
        '+ nome: str',
        '+ nif: str',
        '+ bi: str',
        '+ tipo_cliente: str',
        '+ status: str',
        '+ saldo_atual: Decimal',
        '+ tarifa: Tarifa',
    ], ['+ save()', '+ __str__()', '+ get_tipo_cliente_display()'], C_BLUE_DARK)

    # Column 3
    p_contrato = draw_class_box(10.8, 0, 'Contrato', [
        '+ id: int',
        '+ codigo_contrato: str',
        '+ cliente: Cliente',
        '+ data_inicio: date',
        '+ data_fim: date',
        '+ status: str',
    ], ['+ save()', '+ __str__()'], C_GREEN)

    p_contador = draw_class_box(10.8, -7.5, 'Contador', [
        '+ id: int',
        '+ numero_serie: str',
        '+ cliente: Cliente',
        '+ status: str',
        '+ endereco_instalacao: str',
    ], ['+ clean()', '+ save()', '+ __str__()'], C_BLUE_MED)

    p_hist = draw_class_box(10.8, -14.5, 'HistoricoManutencao', [
        '+ id: int',
        '+ contador: Contador',
        '+ tipo_manutencao: str',
        '+ data_manutencao: date',
        '+ tecnico: str',
    ], ['+ __str__()'], C_ORANGE)

    # Column 4
    p_fatura = draw_class_box(16.1, 0, 'Fatura', [
        '+ id: int',
        '+ numero_fatura: str',
        '+ cliente: Cliente',
        '+ contador: Contador',
        '+ leitura_anterior: Decimal',
        '+ leitura_atual: Decimal',
        '+ consumo_kwh: Decimal',
        '+ valor_total: Decimal',
        '+ multa_atraso: Decimal',
        '+ status: str',
    ], ['+ save()', '+ __str__()', '+ calcular_multa()'], C_RED)

    p_pagamento = draw_class_box(16.1, -10, 'Pagamento', [
        '+ id: int',
        '+ numero_pagamento: str',
        '+ fatura: Fatura',
        '+ valor_pago: Decimal',
        '+ metodo_pagamento: str',
        '+ data_pagamento: datetime',
    ], ['+ save()', '+ __str__()'], C_RED)

    # Column 5
    p_recarga = draw_class_box(21.4, 0, 'Recarga', [
        '+ id: int',
        '+ numero_recarga: str',
        '+ cliente: Cliente',
        '+ valor: Decimal',
        '+ metodo_pagamento: str',
        '+ status: str',
    ], ['+ save()', '+ __str__()'], C_GREEN)

    p_recibo = draw_class_box(21.4, -7.5, 'Recibo', [
        '+ id: int',
        '+ numero_recibo: str',
        '+ cliente: Cliente',
        '+ fatura: Fatura',
        '+ recarga: Recarga',
        '+ valor: Decimal',
    ], ['+ save()', '+ __str__()'], C_GREEN)

    p_notif = draw_class_box(21.4, -14.5, 'Notificacao', [
        '+ id: int',
        '+ cliente: Cliente',
        '+ tipo: str',
        '+ mensagem: str',
        '+ lida: bool',
    ], ['+ __str__()'], C_ORANGE)

    # Associations
    assoc(ax, p_user['bottom'], p_perfil['top'], '1 : 1')
    assoc(ax, p_tarifa['bottom'], p_cliente['top'], '0..1 : N')
    assoc(ax, p_cliente['right'], p_contrato['left'], '1 : N')
    assoc(ax, p_cliente['right'], (p_contador['left'][0], p_contador['left'][1]), '1 : N')
    assoc(ax, p_cliente['right'], (p_recarga['left'][0], p_recarga['left'][1]), '1 : N')
    assoc(ax, p_contador['bottom'], p_hist['top'], '1 : N')
    assoc(ax, p_contador['right'], p_fatura['left'], '1 : N')
    assoc(ax, p_cliente['right'], (p_fatura['left'][0], p_fatura['left'][1] - 0.5), '1 : N')
    assoc(ax, p_fatura['bottom'], p_pagamento['top'], '1 : N')
    assoc(ax, p_fatura['right'], p_recibo['left'], '1 : N')
    assoc(ax, p_recarga['bottom'], (p_recibo['top'][0] + 0.2, p_recibo['top'][1]), '1 : N')
    assoc(ax, p_cliente['right'], (p_notif['left'][0], p_notif['left'][1]), '1 : N')

    plt.tight_layout(pad=0.5)
    fig.savefig('static/diagrams/2_diagrama_classes.png', dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("✓ 2_diagrama_classes.png")


# ═══════════════════════════════════════════════════════════════════════════
# 3. DIAGRAMA DE RELACIONAMENTO ENTRE MÓDULOS
# ═══════════════════════════════════════════════════════════════════════════

def draw_relationship():
    fig, ax = plt.subplots(figsize=(20, 14))
    ax.set_xlim(0, 20)
    ax.set_ylim(-12, 1.5)
    ax.axis('off')
    fig.patch.set_facecolor('#f7f9fc')
    ax.set_facecolor('#f7f9fc')

    ax.text(10, 1.1, 'Diagrama de Relacionamento entre Módulos',
            ha='center', va='center', fontsize=18, fontweight='bold', color=C_BLUE_DARK)
    ax.text(10, 0.5, 'Sistema de Gestão de Energia — Arquitectura Django',
            ha='center', va='center', fontsize=11, color=C_GRAY)

    def mod_box(x, y, w, h, title, items, hcolor, bcolor):
        # Shadow
        ax.add_patch(FancyBboxPatch((x + 0.08, y - h - 0.08), w, h,
                                    boxstyle='round,pad=0.06', linewidth=0,
                                    facecolor='#bbbbbb', zorder=1))
        # Border + body
        ax.add_patch(FancyBboxPatch((x, y - h), w, h,
                                    boxstyle='round,pad=0.06', linewidth=2,
                                    edgecolor=hcolor, facecolor=bcolor, zorder=2))
        # Header band
        ax.add_patch(FancyBboxPatch((x, y - 0.65), w, 0.65,
                                    boxstyle='round,pad=0.03', linewidth=0,
                                    facecolor=hcolor, zorder=3))
        ax.text(x + w / 2, y - 0.32, title, ha='center', va='center',
                fontsize=11, fontweight='bold', color=C_WHITE, zorder=4)
        # Items
        for i, item in enumerate(items):
            iy = y - 0.65 - 0.45 * (i + 0.7)
            ax.text(x + 0.18, iy, f'• {item}', ha='left', va='center',
                    fontsize=8, color='#1a2a3a', zorder=4)
        cx = x + w / 2
        return dict(top=(cx, y), bottom=(cx, y - h),
                    left=(x, y - h / 2), right=(x + w, y - h / 2))

    def rel_arrow(ax, p1, p2, label='', bidirectional=False, color=C_BLUE_MED, rad=0.0):
        style = '<->' if bidirectional else '->'
        ax.annotate('', xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle=style, color=color, lw=1.8,
                                    connectionstyle=f'arc3,rad={rad}'), zorder=5)
        if label:
            mx = (p1[0] + p2[0]) / 2
            my = (p1[1] + p2[1]) / 2
            ax.text(mx, my + 0.18, label, ha='center', va='bottom',
                    fontsize=7.5, color=color, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.25', fc=C_WHITE, ec=color, lw=0.7),
                    zorder=6)

    W = 5.0
    # ── Módulos ──────────────────────────────────────────────────────────
    p_auth = mod_box(7.5, 0, W, 3.2, 'AUTH / UTILIZADORES',
        ['User (Django Auth)', 'Perfil (Tipo: Admin/Op/Fin/Cliente)',
         'Autenticação + Permissões'],
        C_PURPLE, C_PURPLE_L)

    p_clientes = mod_box(0.5, -5.5, W, 4.0, 'MÓDULO CLIENTES',
        ['Cliente (Pré-pago / Pós-pago)', 'Contrato', 'Tarifa',
         'Gestão de saldo', 'Validação de tipo'],
        C_BLUE_DARK, C_BLUE_LIGHT)

    p_equipamentos = mod_box(7.5, -5.5, W, 4.0, 'MÓDULO EQUIPAMENTOS',
        ['Contador (só Pré-pago)', 'Cartão de Recarga',
         'Histórico Manutenção', 'Controlo de estado'],
        C_BLUE_MED, '#dce9f5')

    p_pagamentos = mod_box(14.5, -5.5, W, 4.0, 'MÓDULO PAGAMENTOS',
        ['Fatura (Pós-pago)', 'Recarga (Pré-pago)',
         'Pagamento + Multa automática', 'Recibo + Notificação'],
        C_RED, C_RED_L)

    p_relatorios = mod_box(7.5, -11, W, 3.5, 'MÓDULO RELATÓRIOS',
        ['PDF (ReportLab Platypus)', 'Excel (openpyxl)',
         'Tipos: Clientes / Pagamentos / Consumo',
         'Financeiro Diário e Mensal'],
        C_GREEN, C_GREEN_L)

    # ── Relationships ─────────────────────────────────────────────────────
    rel_arrow(ax, p_auth['bottom'], p_clientes['top'], 'gere', bidirectional=False, color=C_PURPLE)
    rel_arrow(ax, p_auth['bottom'], p_equipamentos['top'], 'autentica', bidirectional=False, color=C_PURPLE)
    rel_arrow(ax, p_auth['bottom'], p_pagamentos['top'], 'autentica', bidirectional=False, color=C_PURPLE)

    rel_arrow(ax, p_clientes['right'], p_equipamentos['left'], 'associa\nContador', color=C_BLUE_DARK, rad=0.0)
    rel_arrow(ax, p_clientes['right'], (p_pagamentos['left'][0], p_pagamentos['left'][1] - 0.3), 'emite\nFatura/Recarga', color=C_BLUE_DARK, rad=0.0)
    rel_arrow(ax, p_equipamentos['right'], p_pagamentos['left'], 'regista\nConsumo', color=C_BLUE_MED, rad=0.0)

    rel_arrow(ax, p_clientes['bottom'], (p_relatorios['left'][0] + 0.5, p_relatorios['left'][1]), 'dados', color=C_BLUE_DARK, rad=0.1)
    rel_arrow(ax, p_pagamentos['bottom'], (p_relatorios['right'][0] - 0.5, p_relatorios['right'][1]), 'dados', color=C_RED, rad=-0.1)
    rel_arrow(ax, p_equipamentos['bottom'], p_relatorios['top'], 'dados', color=C_BLUE_MED)

    # Database
    ax.add_patch(FancyBboxPatch((8.5, -14.5), 3.0, 1.0,
                                boxstyle='round,pad=0.1', linewidth=1.5,
                                edgecolor=C_GRAY, facecolor='#ecf0f1', zorder=2))
    ax.text(10.0, -14.0, '🗄  SQLite / PostgreSQL', ha='center', va='center',
            fontsize=9, color=C_GRAY, fontweight='bold', zorder=3)

    for px, py in [(5.0, -9.5), (10.0, -9.5), (10.0, -9.5), (17.0, -9.5)]:
        ax.annotate('', xy=(10.0, -13.5), xytext=(px, py),
                    arrowprops=dict(arrowstyle='->', color=C_GRAY, lw=1.0,
                                    linestyle='dashed',
                                    connectionstyle='arc3,rad=0.0'), zorder=4)

    plt.tight_layout(pad=0.5)
    fig.savefig('static/diagrams/3_diagrama_relacionamento.png', dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("✓ 3_diagrama_relacionamento.png")


# ═══════════════════════════════════════════════════════════════════════════
# 4. DIAGRAMA DE CASOS DE USO
# ═══════════════════════════════════════════════════════════════════════════

def draw_usecase():
    fig, ax = plt.subplots(figsize=(22, 18))
    ax.set_xlim(0, 22)
    ax.set_ylim(-17, 1.5)
    ax.axis('off')
    fig.patch.set_facecolor('#f7f9fc')
    ax.set_facecolor('#f7f9fc')

    ax.text(11, 1.1, 'Diagrama de Casos de Uso',
            ha='center', va='center', fontsize=18, fontweight='bold', color=C_BLUE_DARK)
    ax.text(11, 0.5, 'Sistema de Gestão de Energia',
            ha='center', va='center', fontsize=11, color=C_GRAY)

    def actor(ax, x, y, name, color=C_BLUE_DARK):
        # Head
        ax.add_patch(plt.Circle((x, y), 0.28, color=color, zorder=3))
        # Body
        ax.plot([x, x], [y - 0.28, y - 1.0], color=color, lw=2, zorder=3)
        # Arms
        ax.plot([x - 0.45, x + 0.45], [y - 0.55, y - 0.55], color=color, lw=2, zorder=3)
        # Legs
        ax.plot([x, x - 0.35], [y - 1.0, y - 1.55], color=color, lw=2, zorder=3)
        ax.plot([x, x + 0.35], [y - 1.0, y - 1.55], color=color, lw=2, zorder=3)
        ax.text(x, y - 1.8, name, ha='center', va='top', fontsize=8.5,
                fontweight='bold', color=color, zorder=3)

    def use_case(ax, x, y, w, h, text, color=C_BLUE_MED, fc=C_BLUE_LIGHT):
        ax.add_patch(mpatches.Ellipse((x, y), w, h, linewidth=1.5,
                                      edgecolor=color, facecolor=fc, zorder=2))
        # Wrap long text
        words = text.split(' ')
        lines = []
        cur = ''
        for w_ in words:
            if len(cur) + len(w_) + 1 > 16:
                lines.append(cur.strip())
                cur = w_ + ' '
            else:
                cur += w_ + ' '
        lines.append(cur.strip())
        ax.text(x, y, '\n'.join(lines), ha='center', va='center',
                fontsize=7.5, color='#1a2a3a', zorder=3,
                multialignment='center', linespacing=1.3)
        return (x, y)

    def connect(ax, actor_pos, uc_pos, color=C_LINE):
        ax.plot([actor_pos[0], uc_pos[0]], [actor_pos[1], uc_pos[1]],
                color=color, lw=1.2, zorder=1, alpha=0.7)

    def include_arrow(ax, p1, p2, label='«include»'):
        ax.annotate('', xy=p2, xytext=p1,
                    arrowprops=dict(arrowstyle='->', color=C_GRAY, lw=1.0,
                                    linestyle='dashed',
                                    connectionstyle='arc3,rad=0.0'), zorder=3)
        mx = (p1[0] + p2[0]) / 2
        my = (p1[1] + p2[1]) / 2 + 0.1
        ax.text(mx, my, label, ha='center', va='bottom', fontsize=6.5,
                color=C_GRAY, style='italic')

    # ── System boundary ───────────────────────────────────────────────────
    ax.add_patch(FancyBboxPatch((3.2, -15.8), 15.6, 16.2,
                                boxstyle='round,pad=0.15', linewidth=2.5,
                                edgecolor=C_BLUE_MED, facecolor='#f0f6ff',
                                zorder=0, alpha=0.6))
    ax.text(11.0, -15.5, 'Sistema de Gestão de Energia',
            ha='center', va='center', fontsize=9, color=C_BLUE_MED,
            style='italic')

    # ── Actors ────────────────────────────────────────────────────────────
    actor(ax, 1.2, 0, 'Administrador', C_PURPLE)
    actor(ax, 1.2, -6.5, 'Operador', C_BLUE_MED)
    actor(ax, 20.8, -3.0, 'Financeiro', C_GREEN)
    actor(ax, 20.8, -10.5, 'Cliente\n(Sistema)', C_ORANGE)

    # ── Use Cases — Autenticação (top) ────────────────────────────────────
    uc_login    = use_case(ax, 11, -0.5, 3.2, 0.8, 'Login no Sistema')

    # ── Use Cases — Módulo Clientes ───────────────────────────────────────
    ax.text(6.2, -1.5, '── Gestão de Clientes ──', fontsize=8, color=C_BLUE_DARK,
            fontweight='bold', style='italic')
    uc_cad_cli  = use_case(ax, 5.5, -2.5, 3.4, 0.8, 'Cadastrar Cliente')
    uc_edit_cli = use_case(ax, 9.5, -2.5, 3.4, 0.8, 'Editar/Inactivar Cliente')
    uc_tarifa   = use_case(ax, 13.5, -2.5, 3.2, 0.8, 'Gerir Tarifas')
    uc_contrato = use_case(ax, 17.0, -2.5, 3.0, 0.8, 'Criar Contrato')

    # ── Use Cases — Módulo Equipamentos ──────────────────────────────────
    ax.text(5.5, -4.0, '── Gestão de Equipamentos ──', fontsize=8, color=C_BLUE_MED,
            fontweight='bold', style='italic')
    uc_contador = use_case(ax, 5.5, -5.0, 3.4, 0.8, 'Registar Contador')
    uc_manut    = use_case(ax, 9.5, -5.0, 3.4, 0.8, 'Registar Manutenção')
    uc_cartao   = use_case(ax, 13.5, -5.0, 3.2, 0.8, 'Gerir Cartões Recarga')
    uc_suspender= use_case(ax, 17.0, -5.0, 3.0, 0.8, 'Suspender Contador')

    # ── Use Cases — Módulo Pagamentos ─────────────────────────────────────
    ax.text(4.5, -6.5, '── Pagamentos e Faturação ──', fontsize=8, color=C_RED,
            fontweight='bold', style='italic')
    uc_fatura   = use_case(ax, 4.8, -7.8, 3.4, 0.8, 'Emitir Fatura', C_RED, C_RED_L)
    uc_fatura_auto = use_case(ax, 8.7, -7.8, 3.4, 0.8, 'Gerar Faturas Automáticas', C_RED, C_RED_L)
    uc_pagto    = use_case(ax, 12.5, -7.8, 3.4, 0.8, 'Registar Pagamento', C_RED, C_RED_L)
    uc_multa    = use_case(ax, 16.3, -7.8, 3.2, 0.8, 'Calcular Multa por Atraso', C_RED, C_RED_L)
    uc_recarga  = use_case(ax, 4.8, -9.5, 3.4, 0.8, 'Registar Recarga', C_GREEN, C_GREEN_L)
    uc_recibo   = use_case(ax, 8.7, -9.5, 3.4, 0.8, 'Emitir Recibo', C_GREEN, C_GREEN_L)
    uc_notif    = use_case(ax, 12.5, -9.5, 3.4, 0.8, 'Enviar Notificação\nSaldo Baixo', C_ORANGE, C_ORANGE_L)
    uc_divida   = use_case(ax, 16.3, -9.5, 3.2, 0.8, 'Controlo de Dívida', C_RED, C_RED_L)

    # ── Use Cases — Relatórios ────────────────────────────────────────────
    ax.text(5.5, -11.0, '── Relatórios ──', fontsize=8, color=C_GREEN,
            fontweight='bold', style='italic')
    uc_rel_cli  = use_case(ax, 5.8, -12.0, 3.2, 0.8, 'Relatório Clientes', C_GREEN, C_GREEN_L)
    uc_rel_fin  = use_case(ax, 9.8, -12.0, 3.4, 0.8, 'Relatório Financeiro', C_GREEN, C_GREEN_L)
    uc_rel_cons = use_case(ax, 13.8, -12.0, 3.4, 0.8, 'Relatório Consumo', C_GREEN, C_GREEN_L)
    uc_pdf      = use_case(ax, 7.0, -13.8, 3.0, 0.8, 'Exportar PDF', C_GREEN, C_GREEN_L)
    uc_excel    = use_case(ax, 12.0, -13.8, 3.0, 0.8, 'Exportar Excel', C_GREEN, C_GREEN_L)

    # ── Dashboard ─────────────────────────────────────────────────────────
    uc_dash    = use_case(ax, 17.5, -12.5, 3.2, 0.8, 'Ver Dashboard', C_BLUE_MED, '#dce9f5')

    # ── Connections — Admin ───────────────────────────────────────────────
    admin_pos = (1.2, -1.0)
    for uc in [uc_login, uc_cad_cli, uc_edit_cli, uc_tarifa, uc_contrato,
               uc_contador, uc_manut, uc_cartao, uc_suspender,
               uc_fatura, uc_fatura_auto, uc_rel_cli, uc_rel_fin, uc_rel_cons, uc_dash]:
        connect(ax, admin_pos, uc, C_PURPLE)

    # ── Connections — Operador ────────────────────────────────────────────
    oper_pos = (1.2, -7.0)
    for uc in [uc_login, uc_cad_cli, uc_contador, uc_manut, uc_cartao,
               uc_fatura, uc_fatura_auto, uc_recarga, uc_recibo,
               uc_pagto, uc_suspender, uc_divida]:
        connect(ax, oper_pos, uc, C_BLUE_MED)

    # ── Connections — Financeiro ──────────────────────────────────────────
    fin_pos = (20.8, -3.6)
    for uc in [uc_login, uc_rel_cli, uc_rel_fin, uc_rel_cons,
               uc_pdf, uc_excel, uc_dash, uc_fatura, uc_pagto, uc_multa]:
        connect(ax, fin_pos, uc, C_GREEN)

    # ── Connections — Cliente ─────────────────────────────────────────────
    cli_pos = (20.8, -11.1)
    for uc in [uc_login, uc_notif, uc_recibo, uc_divida]:
        connect(ax, cli_pos, uc, C_ORANGE)

    # ── Include arrows ────────────────────────────────────────────────────
    include_arrow(ax, uc_pagto, uc_multa, '«include»')
    include_arrow(ax, uc_recarga, uc_notif, '«include»')
    include_arrow(ax, uc_fatura, uc_recibo, '«include»')
    include_arrow(ax, uc_rel_cli, uc_pdf, '«extend»')
    include_arrow(ax, uc_rel_fin, uc_excel, '«extend»')

    plt.tight_layout(pad=0.5)
    fig.savefig('static/diagrams/4_diagrama_caso_uso.png', dpi=150, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    plt.close(fig)
    print("✓ 4_diagrama_caso_uso.png")


# ─────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("A gerar diagramas...")
    draw_er()
    draw_class()
    draw_relationship()
    draw_usecase()
    print("\nTodos os diagramas guardados em static/diagrams/")
