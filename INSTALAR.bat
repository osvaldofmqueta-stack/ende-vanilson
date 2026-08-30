@echo off
setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
cls
color 0B

echo.
echo  ===============================================================
echo    SISTEMA DE GESTAO DE ENERGIA  -  INSTALADOR AUTOMATICO
echo  ===============================================================
echo.

:: ---- Verificar Python ----
where python >nul 2>&1
if errorlevel 1 goto python_not_found

python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if errorlevel 1 goto python_version_error

for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PYVER=%%v"
echo  [OK] Python %PYVER% encontrado.
echo.

if not exist "manage.py" goto project_not_found
if not exist "requirements.txt" goto requirements_not_found

:: ---- Ambiente virtual ----
echo  [1/5] A verificar ambiente virtual...
if exist "venv\Scripts\python.exe" (
    echo  [OK] Ambiente virtual ja existe.
) else (
    echo  [INFO] A criar ambiente virtual...
    python -m venv venv
    if errorlevel 1 goto venv_error
    echo  [OK] Ambiente virtual criado.
)
set "PYTHON=venv\Scripts\python.exe"

:: ---- Verificar e instalar dependencias ----
echo.
echo  [2/5] A verificar dependencias...
"%PYTHON%" -c "import django" >nul 2>&1
if not errorlevel 1 (
    echo  [OK] Django ja esta instalado.
) else (
    echo  [INFO] Django nao encontrado. Sera instalado agora.
)

:: Sincronizar todas as dependencias, incluindo Django
call :install_dependencies
if errorlevel 1 goto dependencies_failed

:: Confirmar Django depois da instalacao
"%PYTHON%" -c "import django; print('  Django ' + django.get_version() + ' pronto.')" 2>nul
if errorlevel 1 goto django_error
echo  [OK] Dependencias verificadas.

:: ---- Base de dados ----
echo.
echo  [3/5] A configurar base de dados...
"%PYTHON%" manage.py migrate --run-syncdb
if errorlevel 1 goto database_error
echo  [OK] Base de dados configurada.

:: ---- Utilizadores ----
echo.
echo  [4/5] A configurar utilizadores...
echo  A gerar palavras-passe seguras automaticamente.
echo  Numa reinstalacao, as passwords serao renovadas.
set "CREDENTIALS_FILE=%~dp0CREDENCIAIS_ACESSO.txt"
"%PYTHON%" manage.py criar_utilizadores_padrao --reset-existing --auto-passwords --credentials-file "%CREDENTIALS_FILE%"
if errorlevel 1 goto users_error

:: ---- Ficheiros estaticos ----
echo.
echo  [5/5] A preparar ficheiros estaticos...
"%PYTHON%" manage.py collectstatic --noinput --clear
if errorlevel 1 goto static_error
echo  [OK] Instalacao completa!

echo.
echo  ===============================================================
echo    INSTALACAO CONCLUIDA COM SUCESSO!
echo  ===============================================================
echo.
echo   O sistema vai abrir no navegador em alguns segundos...
echo.
echo   Endereco local: http://localhost:8000
echo   Credenciais guardadas em: CREDENCIAIS_ACESSO.txt
echo   Para parar o servidor: pressione Ctrl+C
echo.
echo  ===============================================================
echo.
if exist "%CREDENTIALS_FILE%" (
    type "%CREDENTIALS_FILE%"
)
echo.

:: Abrir navegador apos 3 segundos
start "" /b cmd /c "timeout /t 3 /nobreak >nul & start "" http://localhost:8000"

:: Iniciar servidor
"%PYTHON%" manage.py runserver 0.0.0.0:8000
set "EXIT_CODE=%errorlevel%"
endlocal & exit /b %EXIT_CODE%

:install_dependencies
set "ATTEMPT=1"
:install_dependencies_attempt
echo.
echo  [INFO] Tentativa %ATTEMPT% de 3. O download pode demorar alguns minutos...
"%PYTHON%" -m pip install -r requirements.txt --prefer-binary --retries 8 --timeout 180 --disable-pip-version-check
if not errorlevel 1 exit /b 0
if %ATTEMPT% GEQ 3 exit /b 1
set /a ATTEMPT+=1
echo.
echo  [AVISO] A ligacao foi interrompida. Nova tentativa em 15 segundos...
timeout /t 15 /nobreak >nul
goto install_dependencies_attempt

:python_not_found
echo  [ERRO] Python nao foi encontrado no computador.
echo.
echo  Instale Python 3.11 ou superior em:
echo  https://www.python.org/downloads/
echo  Durante a instalacao, marque "Add Python to PATH".
goto fail

:python_version_error
echo  [ERRO] Este projeto precisa do Python 3.11 ou superior.
echo  A versao encontrada nao e compativel.
goto fail

:project_not_found
echo  [ERRO] manage.py nao foi encontrado.
echo  Execute este ficheiro dentro da pasta principal do projeto.
goto fail

:requirements_not_found
echo  [ERRO] requirements.txt nao foi encontrado.
echo  Confirme que o projeto foi extraido completamente.
goto fail

:venv_error
echo  [ERRO] Nao foi possivel criar o ambiente virtual.
goto fail

:dependencies_failed
echo.
echo  [ERRO] Nao foi possivel instalar as dependencias apos 3 tentativas.
echo  Verifique a Internet, VPN, proxy ou antivirus e tente novamente.
goto fail

:django_error
echo.
echo  [ERRO] O Django nao ficou disponivel apos a instalacao.
goto fail

:database_error
echo  [ERRO] Falha ao configurar a base de dados.
goto fail

:users_error
echo  [ERRO] Falha ao configurar os utilizadores.
goto fail

:static_error
echo  [ERRO] Falha ao preparar os ficheiros estaticos.
goto fail

:fail
echo.
echo  A instalacao nao foi concluida. Corrija o problema indicado e execute
echo  INSTALAR.bat novamente.
if defined CREDENTIALS_FILE if exist "%CREDENTIALS_FILE%" del /q "%CREDENTIALS_FILE%" >nul 2>&1
pause
endlocal & exit /b 1