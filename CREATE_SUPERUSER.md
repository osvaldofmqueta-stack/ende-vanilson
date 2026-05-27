# Sistema de Gestão de Energia

## Criar Superusuário (Admin)

Para acessar o painel administrativo, você precisa criar um superusuário.

Execute o comando:

```bash
python manage.py createsuperuser
```

Siga as instruções para definir:
- Username (nome de usuário)
- Email (pode deixar em branco)
- Password (senha)

## Acesso ao Sistema

Após criar o superusuário, você pode acessar:

- **Home Page**: http://localhost:5000/ (ou o domínio do Replit)
- **Dashboard**: http://localhost:5000/dashboard/
- **Admin Panel**: http://localhost:5000/admin/

## Funcionalidades Implementadas

### Módulos Principais

1. **Clientes** (`/admin/clientes/`)
   - Cadastro completo de clientes (nome, NIF, BI, morada, telefone, email)
   - Tipos: Pré-pago e Pós-pago
   - Geração automática de número de cliente (CLI-XXXXXX)
   - Controle de saldo para clientes pré-pagos

2. **Contratos** (`/admin/clientes/contrato/`)
   - Geração automática de código de contrato (CTR-ANO-XXXXXXXX)
   - Vinculação com cliente
   - Definição de tarifa por kWh

3. **Contadores/Equipamentos** (`/admin/equipamentos/`)
   - Registro de contadores (medidores)
   - Tipos: Pré-pago e Pós-pago
   - Atribuição a cliente e endereço
   - Histórico de manutenção
   - Cartões de recarga

4. **Pagamentos** (`/admin/pagamentos/`)
   - Recargas (pré-pago) com geração automática de número
   - Faturas (pós-pago) com cálculo automático de consumo
   - Recibos com geração automática
   - Sistema de notificações (saldo baixo, faturas vencidas, etc.)

5. **Relatórios** (`/admin/relatorios/`)
   - Registro de relatórios gerados
   - Tipos: clientes ativos/inativos, consumo, pagamentos, etc.

### Recursos Implementados

✅ Geração automática de números de cliente e códigos de contrato  
✅ Sistema de pré-pago e pós-pago  
✅ Gestão de contadores com histórico de manutenção  
✅ Sistema de recargas e faturas  
✅ Sistema de notificações  
✅ Dashboard com estatísticas  
✅ Interface administrativa completa  
✅ Base de dados PostgreSQL configurada  

### Próximas Funcionalidades (Fase 2)

- Geração de PDFs (faturas, recibos, relatórios)
- Importação de clientes via PDF
- Integração com Multicaixa e ATM
- Sistema de reclamações
- Faturas com QR Code
- Envio de relatórios automáticos por email
- Sistema de reconexão automática

## Estrutura do Projeto

```
energia_gestao/          # Configurações do projeto
clientes/                # App de gestão de clientes e contratos
equipamentos/            # App de gestão de contadores e equipamentos
pagamentos/              # App de gestão de pagamentos, recargas e faturas
relatorios/              # App de gestão de relatórios
templates/               # Templates HTML
static/                  # Arquivos estáticos (CSS, JS, imagens)
manage.py               # Script principal do Django (na raiz)
```
