#!/bin/bash

# ===============================================================
#   SISTEMA DE GESTAO DE ENERGIA  -  INSTALADOR (Linux / Mac)
# ===============================================================

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

clear
echo ""
echo "  ============================================================="
echo "    SISTEMA DE GESTAO DE ENERGIA  -  INSTALADOR AUTOMATICO"
echo "  ============================================================="
echo ""

# ---- Verificar Python ----
PYTHON_CMD=""
for cmd in python3.11 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        VER=$("$cmd" --version 2>&1 | awk '{print $2}')
        MAJOR=$(echo "$VER" | cut -d. -f1)
        MINOR=$(echo "$VER" | cut -d. -f2)
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
            PYTHON_CMD="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "  ${RED}[ERRO]${NC} Python 3.8+ nao encontrado!"
    echo ""
    echo "  Instale Python:"
    echo "    Ubuntu/Debian : sudo apt install python3 python3-venv python3-pip"
    echo "    Mac           : brew install python3"
    echo "    Ou visite     : https://www.python.org/downloads/"
    echo ""
    exit 1
fi

echo -e "  ${GREEN}[OK]${NC} Python $($PYTHON_CMD --version 2>&1 | awk '{print $2}') encontrado."
echo ""

# ---- Ambiente virtual ----
if [ ! -d "venv" ]; then
    echo "  [1/5] A criar ambiente virtual..."
    $PYTHON_CMD -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "  ${RED}[ERRO]${NC} Falha ao criar ambiente virtual."
        echo "  Tente: sudo apt install python3-venv"
        exit 1
    fi
    echo -e "  ${GREEN}[OK]${NC} Ambiente virtual criado."
else
    echo "  [1/5] Ambiente virtual ja existe. A continuar..."
fi

source venv/bin/activate

# ---- Instalar dependencias ----
echo ""
echo "  [2/5] A instalar dependencias (pode demorar 2-3 minutos)..."
pip install -r requirements_local.txt --quiet --disable-pip-version-check
if [ $? -ne 0 ]; then
    echo -e "  ${RED}[ERRO]${NC} Falha na instalacao das dependencias."
    exit 1
fi
echo -e "  ${GREEN}[OK]${NC} Dependencias instaladas."

# ---- Base de dados ----
echo ""
echo "  [3/5] A configurar base de dados..."
python manage.py migrate --run-syncdb >/dev/null 2>&1
python manage.py migrate
if [ $? -ne 0 ]; then
    echo -e "  ${RED}[ERRO]${NC} Falha na configuracao da base de dados."
    exit 1
fi
echo -e "  ${GREEN}[OK]${NC} Base de dados configurada."

# ---- Utilizadores padrao ----
echo ""
echo "  [4/5] A criar/redefinir utilizadores padrao..."
python manage.py redefinir_senhas

# ---- Ficheiros estaticos ----
echo ""
echo "  [5/5] A preparar ficheiros estaticos..."
python manage.py collectstatic --noinput --clear >/dev/null 2>&1
echo -e "  ${GREEN}[OK]${NC} Instalacao completa!"

echo ""
echo "  ============================================================="
echo -e "  ${GREEN}  INSTALACAO CONCLUIDA COM SUCESSO!${NC}"
echo "  ============================================================="
echo ""
echo "   Credenciais de acesso:"
echo "   ---------------------------------------------------------"
echo "    Administrador :  admin       /  admin@2025"
echo "    Financeiro    :  financeiro  /  fin@2025"
echo "    Operador      :  operador    /  oper@2025"
echo "   ---------------------------------------------------------"
echo ""
echo "   Endereco local: http://localhost:8000"
echo "   Para parar o servidor: pressione Ctrl+C"
echo ""
echo "  ============================================================="
echo ""

# Abrir navegador automaticamente
(sleep 2 && (
    if command -v xdg-open &>/dev/null; then
        xdg-open http://localhost:8000
    elif command -v open &>/dev/null; then
        open http://localhost:8000
    fi
)) &

# Iniciar servidor
python manage.py runserver 0.0.0.0:8000
