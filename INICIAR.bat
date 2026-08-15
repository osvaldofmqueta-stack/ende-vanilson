@echo off
chcp 65001 >nul
cls
color 0A

echo.
echo  ===============================================================
echo    SISTEMA DE GESTAO DE ENERGIA  -  INICIAR
echo  ===============================================================
echo.

:: Verificar instalacao
if not exist "venv\" (
    echo  [ERRO] Sistema nao instalado.
    echo  Por favor execute primeiro: INSTALAR.bat
    echo.
    pause
    exit /b 1
)

:: Verificar base de dados
if not exist "db.sqlite3" (
    echo  [AVISO] Base de dados nao encontrada. A executar migracao...
    call venv\Scripts\activate.bat
    python manage.py migrate >nul 2>&1
    python manage.py criar_utilizadores_padrao
)

call venv\Scripts\activate.bat

echo   Enderecos de acesso:
echo   ----------------------------------------------------------
echo    Local:     http://localhost:8000
echo    Na rede:   http://%COMPUTERNAME%:8000
echo   ----------------------------------------------------------
echo.
echo   Utilize as palavras-passe definidas durante a instalacao.
echo.
echo   Para parar o servidor: pressione Ctrl+C
echo.
echo  ===============================================================
echo.

:: Abrir navegador automaticamente
start /b cmd /c "timeout /t 2 >nul & start http://localhost:8000"

:: Iniciar servidor
python manage.py runserver 0.0.0.0:8000

pause
