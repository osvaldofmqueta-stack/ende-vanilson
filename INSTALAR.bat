@echo off
chcp 65001 >nul
cls
color 0B

echo.
echo  ===============================================================
echo    SISTEMA DE GESTAO DE ENERGIA  -  INSTALADOR AUTOMATICO
echo  ===============================================================
echo.

:: ---- Verificar Python ----
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERRO] Python nao encontrado no seu computador!
    echo.
    echo  Por favor:
    echo    1. Abra o site: https://www.python.org/downloads/
    echo    2. Descarregue Python 3.11 ou superior
    echo    3. Durante a instalacao, marque "Add Python to PATH"
    echo    4. Apos instalar, execute este ficheiro novamente
    echo.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo  [OK] Python %PYVER% encontrado.
echo.

:: ---- Ambiente virtual ----
if not exist "venv\" (
    echo  [1/5] A criar ambiente virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo  [ERRO] Falha ao criar ambiente virtual.
        pause & exit /b 1
    )
    echo  [OK] Ambiente virtual criado.
) else (
    echo  [1/5] Ambiente virtual ja existe. A continuar...
)
call venv\Scripts\activate.bat

:: ---- Instalar dependencias ----
echo.
echo  [2/5] A instalar dependencias (pode demorar 2-3 minutos)...
pip install -r requirements_local.txt --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo  [ERRO] Falha na instalacao das dependencias.
    pause & exit /b 1
)
echo  [OK] Dependencias instaladas.

:: ---- Base de dados ----
echo.
echo  [3/5] A configurar base de dados...
python manage.py migrate --run-syncdb >nul 2>&1
python manage.py migrate
if %errorlevel% neq 0 (
    echo  [ERRO] Falha na configuracao da base de dados.
    pause & exit /b 1
)
echo  [OK] Base de dados configurada.

:: ---- Utilizadores padrao ----
echo.
echo  [4/5] A criar utilizadores padrao...
python manage.py criar_utilizadores_padrao
echo.

:: ---- Ficheiros estaticos ----
echo  [5/5] A preparar ficheiros estaticos...
python manage.py collectstatic --noinput --clear >nul 2>&1
echo  [OK] Instalacao completa!

echo.
echo  ===============================================================
echo    INSTALACAO CONCLUIDA COM SUCESSO!
echo  ===============================================================
echo.
echo   O sistema vai abrir no navegador em alguns segundos...
echo.
echo   Credenciais de acesso:
echo   ----------------------------------------------------------
echo    Administrador :  admin       /  admin@2025
echo    Financeiro    :  financeiro  /  fin@2025
echo    Operador      :  operador    /  oper@2025
echo   ----------------------------------------------------------
echo.
echo   Endereco local: http://localhost:8000
echo   Para parar o servidor: pressione Ctrl+C
echo.
echo  ===============================================================
echo.

:: Abrir navegador apos 3 segundos
start /b cmd /c "timeout /t 3 >nul & start http://localhost:8000"

:: Iniciar servidor
python manage.py runserver 0.0.0.0:8000

pause
