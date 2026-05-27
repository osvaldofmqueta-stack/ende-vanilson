# Sistema de Gestão de Energia

## Visão Geral
Sistema completo de gestão de energia desenvolvido com Python Django para gerenciar clientes pré-pagos e pós-pagos, contadores, pagamentos, faturas e relatórios.

## Última Atualização
**Data:** 14 de Outubro de 2025  
**Status:** MVP Implementado e Funcional

## Estrutura do Projeto

### Aplicações Django
- **clientes/** - Gestão de clientes e contratos
- **equipamentos/** - Gestão de contadores e equipamentos
- **pagamentos/** - Gestão de pagamentos, recargas, faturas e notificações
- **relatorios/** - Gestão de relatórios

### Configuração
- **manage.py** - Na raiz do projeto (conforme solicitado)
- **energia_gestao/** - Configurações principais do Django
- **templates/** - Templates HTML globais
- **static/** - Arquivos estáticos (CSS, JS, imagens)

## Funcionalidades Implementadas

### ✅ Módulo de Clientes
- Cadastro completo (nome, NIF, BI, morada, telefone, email)
- Tipos: Pré-pago e Pós-pago
- Geração automática de número de cliente (CLI-XXXXXX)
- Controle de saldo para clientes pré-pagos
- Sistema de contratos com código automático (CTR-ANO-XXXXXXXX)

### ✅ Módulo de Equipamentos
- Registro de contadores (medidores)
- Tipos: Pré-pago e Pós-pago
- Atribuição a cliente e endereço
- Histórico completo de manutenção
- Sistema de cartões de recarga

### ✅ Módulo de Pagamentos
- Sistema de recargas (pré-pago)
- Sistema de faturas (pós-pago) com cálculo automático
- Geração de recibos
- Sistema de notificações (saldo baixo, faturas vencidas, etc.)
- Métodos de pagamento: Multicaixa, ATM, USSD, App, Cartão, Dinheiro

### ✅ Dashboard e Interface
- Home page com estatísticas em tempo real
- Dashboard administrativo completo
- Interface de administração Django customizada
- Templates responsivos com Bootstrap 5

### ✅ Infraestrutura
- Base de dados PostgreSQL configurada
- Workflow Django configurado (porta 5000)
- Sistema de migração de base de dados
- Configuração de ficheiros estáticos e media

## Características Técnicas

### Geração Automática de Códigos
- **Número de Cliente:** CLI-XXXXXX (sequencial)
- **Código de Contrato:** CTR-ANO-XXXXXXXX (ano + UUID)
- **Número de Recarga:** REC-XXXXXX (UUID)
- **Número de Fatura:** FAT-ANO-XXXXXX (ano + UUID)
- **Número de Recibo:** REC-ANO-XXXXXX (ano + UUID)

### Models com Relacionamentos
- Cliente ↔ Contrato (um para muitos)
- Cliente ↔ Contador (um para muitos)
- Cliente ↔ Fatura/Recarga/Recibo (um para muitos)
- Contador ↔ Histórico de Manutenção (um para muitos)
- Contador ↔ Fatura (um para muitos)

### Cálculos Automáticos
- Consumo kWh = Leitura Atual - Leitura Anterior
- Valor da Fatura com base na tarifa por kWh
- Atualização automática de saldo do cliente

## Como Usar

### 1. Criar Superusuário (Admin)
```bash
python manage.py createsuperuser
```

### 2. Acessar o Sistema
- **Home Page:** http://localhost:5000/
- **Dashboard:** http://localhost:5000/dashboard/
- **Admin Panel:** http://localhost:5000/admin/

### 3. Gestão via Admin
- **/admin/clientes/cliente/** - Gestão de clientes
- **/admin/clientes/contrato/** - Gestão de contratos
- **/admin/equipamentos/contador/** - Gestão de contadores
- **/admin/equipamentos/historicomanutencao/** - Histórico de manutenção
- **/admin/equipamentos/cartaorecarga/** - Cartões de recarga
- **/admin/pagamentos/recarga/** - Recargas
- **/admin/pagamentos/fatura/** - Faturas
- **/admin/pagamentos/recibo/** - Recibos
- **/admin/pagamentos/notificacao/** - Notificações

## Stack Tecnológica

### Backend
- Django 5.2.7
- PostgreSQL (Neon via Replit)
- Django REST Framework 3.16.1
- Django Filter 25.2

### Frontend
- Bootstrap 5.3
- Templates Django
- HTML/CSS/JavaScript

### Bibliotecas
- ReportLab 4.4.4 (preparado para PDFs)
- Pillow 11.3.0 (processamento de imagens)
- python-decouple 3.8 (gestão de configurações)
- psycopg2-binary 2.9.11 (PostgreSQL adapter)

## Próximas Funcionalidades (Fase 2)

### 🔄 Em Planeamento
1. **Geração de PDFs**
   - Faturas em PDF com logo e dados da empresa
   - Recibos em PDF
   - Relatórios mensais em PDF
   - QR Code em faturas para pagamento rápido

2. **Importação de Dados**
   - Importação de clientes via PDF (OCR)
   - Importação em massa via Excel/CSV

3. **Integrações de Pagamento**
   - Integração com Multicaixa Express API
   - Integração com ATM
   - Webhooks para confirmação automática

4. **Sistema de Reclamações**
   - Registro de reclamações
   - Classificação (urgente, normal, baixa)
   - Acompanhamento de estado
   - Painel de desempenho (SLA)

5. **Relatórios Avançados**
   - Consumo médio por área geográfica
   - Relatórios automáticos por email
   - Exportação em Excel/CSV
   - Gráficos e visualizações

6. **Automação**
   - Reconexão automática após pagamento
   - Envio automático de notificações
   - Agendamento de cortes por falta de pagamento
   - Tarefas assíncronas com Celery

## Notas de Desenvolvimento

### Ambiente de Desenvolvimento
- Python 3.11
- Timezone: Africa/Luanda
- Idioma: Português (pt-pt)
- Servidor de desenvolvimento: 0.0.0.0:5000

### Segurança
- Secret keys geridas via python-decouple
- Senhas de base de dados em variáveis de ambiente
- DEBUG mode apenas em desenvolvimento

### Comandos Úteis
```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Executar servidor
python manage.py runserver 0.0.0.0:5000

# Coletar ficheiros estáticos
python manage.py collectstatic
```

## Arquitetura de Dados

### Fluxo Pré-pago
1. Cliente cadastrado como PRE_PAGO
2. Cliente compra recarga (cartão/app/multicaixa)
3. Recarga confirmada → saldo atualizado
4. Consumo deduzido do saldo automaticamente
5. Notificação quando saldo baixo

### Fluxo Pós-pago
1. Cliente cadastrado como POS_PAGO
2. Contador regista consumo mensal
3. Sistema gera fatura automaticamente
4. Cliente paga fatura
5. Recibo gerado automaticamente

## Manutenção e Suporte

### Logs
- Logs do Django em `/tmp/logs/`
- Logs do workflow disponíveis no Replit

### Backup
- Base de dados PostgreSQL com backup automático (Neon)
- Ficheiros de media devem ter backup separado

### Monitoramento
- Dashboard com estatísticas em tempo real
- Notificações de sistema para alertas

---

**Desenvolvido com Django + PostgreSQL + Bootstrap**  
**Replit Environment - Outubro 2025**
