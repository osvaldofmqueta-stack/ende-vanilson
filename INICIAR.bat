@echo off
setlocal EnableExtensions
cd /d "%~dp0"
chcp 65001 >nul
cls
color 0A

echo.
echo  ===============================================================
echo    SISTEMA DE GESTAO DE ENERGIA  -  INICIAR
echo  ===============================================================
echo.

:: Verificar instalacao
if not exist "venv\Scripts\python.exe" (
    echo  [ERRO] Sistema nao instalado.
    echo  Por favor execute primeiro: INSTALAR.bat
    echo.
    pause
    exit /b 1
)
set "PYTHON=venv\Scripts\python.exe"

if not exist "find_free_port.py" (
    echo  [ERRO] find_free_port.py nao foi encontrado.
    echo  Confirme que o projeto foi extraido completamente.
    pause
    exit /b 1
)

:: Verificar base de dados
if not exist "db.sqlite3" (
    echo  [AVISO] Base de dados nao encontrada. A executar migracao...
    "%PYTHON%" manage.py migrate >nul 2>&1
    if errorlevel 1 (
        echo  [ERRO] Nao foi possivel criar a base de dados SQLite.
        pause
        exit /b 1
    )
    "%PYTHON%" manage.py criar_utilizadores_padrao --auto-passwords --credentials-file "%~dp0CREDENCIAIS_ACESSO.txt"
    if errorlevel 1 (
        echo  [ERRO] Nao foi possivel criar os utilizadores.
        pause
        exit /b 1
    )
)

:: Escolher automaticamente uma porta web livre
set "PORT="
for /f "delims=" %%p in ('"%PYTHON%" find_free_port.py 2^>nul') do set "PORT=%%p"
if not defined PORT (
    echo  [ERRO] Nao foi encontrada uma porta livre entre 8000 e 8999.
    echo  Feche algum servidor ou programa local e tente novamente.
    pause
    exit /b 1
)

echo   Enderecos de acesso:
echo   ----------------------------------------------------------
echo    Local:     http://localhost:%PORT%
echo    Na rede:   http://%COMPUTERNAME%:%PORT%
echo   ----------------------------------------------------------
echo.
echo   Consulte CREDENCIAIS_ACESSO.txt na pasta da aplicacao.
echo.
echo   Para parar o servidor: pressione Ctrl+C
echo.
echo  ===============================================================
echo.

:: Abrir navegador automaticamente
start /b cmd /c "timeout /t 2 >nul & start http://localhost:%PORT%"

:: Iniciar servidor
"%PYTHON%" manage.py runserver 0.0.0.0:%PORT%

pause
endlocal
