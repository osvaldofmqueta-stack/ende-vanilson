#!/bin/bash

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

clear
echo ""
echo "  ============================================================="
echo "    SISTEMA DE GESTAO DE ENERGIA"
echo "  ============================================================="
echo ""

if [ ! -d "venv" ]; then
    echo -e "  ${RED}[ERRO]${NC} Sistema nao instalado. Execute primeiro: bash instalar.sh"
    exit 1
fi

source venv/bin/activate

if [ ! -f "db.sqlite3" ]; then
    echo "  [AVISO] Base de dados nao encontrada. A criar..."
    python manage.py migrate >/dev/null 2>&1
    python manage.py criar_utilizadores_padrao
fi

echo "   Endereco: http://localhost:8000"
echo "   Para parar: Ctrl+C"
echo ""
echo "   Utilize as palavras-passe definidas durante a instalacao."
echo ""

(sleep 2 && (
    if command -v xdg-open &>/dev/null; then
        xdg-open http://localhost:8000
    elif command -v open &>/dev/null; then
        open http://localhost:8000
    fi
)) &

python manage.py runserver 0.0.0.0:8000
