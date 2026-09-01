@echo off
:: Quando aberto por duplo clique, manter uma janela de comandos aberta.
:: Isto permite ler qualquer erro mesmo que o instalador termine cedo.
if /i not "%~1"=="__EXECUTAR_INSTALADOR" (
    start "Instalador - Sistema de Gestao de Energia" "%ComSpec%" /d /k call "%~f0" __EXECUTAR_INSTALADOR
    exit /b 0
)

setlocal EnableExtensions
chcp 65001 >nul
cd /d "%~dp0"
set "LOGFILE=%~dp0instalacao.log"
> "%LOGFILE%" echo Inicio da instalacao em %date% %time%
cls
color 0B

echo.
echo  ===============================================================
echo    SISTEMA DE GESTAO DE ENERGIA  -  INSTALADOR AUTOMATICO
echo  ===============================================================
echo    VERSAO CORRIGIDA - DETECAO REAL DO PYTHON
echo.

:: ---- Verificar Python ----
:: Testar o Python de verdade, evitando o atalho da Microsoft Store.
set "PYTHON_CMD="
set "PYVER="
call :try_python "py -3.11"
if not defined PYTHON_CMD call :try_python "py -3"
if not defined PYTHON_CMD call :try_python "python"
if not defined PYTHON_CMD goto python_not_found

echo  [OK] %PYVER% encontrado.
echo.

if not exist "manage.py" goto project_not_found
if not exist "requirements.txt" goto requirements_not_found
if not exist "find_free_port.py" goto port_script_not_found

:: ---- Ambiente virtual ----
echo  [1/5] A verificar ambiente virtual...
if exist "venv\Scripts\python.exe" (
    echo  [OK] Ambiente virtual ja existe.
) else (
    echo  [INFO] A criar ambiente virtual...
    %PYTHON_CMD% -m venv venv 2>>"%LOGFILE%"
    if errorlevel 1 goto venv_error
    echo  [OK] Ambiente virtual criado.
)
set "PYTHON=venv\Scripts\python.exe"
if not exist "%PYTHON%" goto venv_error

:: Confirmar que o ambiente virtual tem pip disponível.
"%PYTHON%" -m pip --version >nul 2>>"%LOGFILE%"
if errorlevel 1 goto pip_error

:: ---- Verificar e instalar dependencias ----
echo.
echo  [2/5] A verificar dependencias...
"%PYTHON%" -c "import django" >nul 2>>"%LOGFILE%"
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
"%PYTHON%" manage.py migrate --run-syncdb 2>>"%LOGFILE%"
if errorlevel 1 goto database_error
echo  [OK] Base de dados configurada.

:: ---- Escolher porta web livre ----
echo.
echo  A procurar uma porta web livre...
set "PORT="
for /f "delims=" %%p in ('"%PYTHON%" find_free_port.py 2^>nul') do set "PORT=%%p"
if not defined PORT goto port_error
echo  [OK] Porta web selecionada: %PORT%

:: ---- Utilizadores ----
echo.
echo  [4/5] A configurar utilizadores...
echo  Numa instalacao nova, defina as palavras-passe quando solicitado.
echo  Numa reinstalacao, as palavras-passe existentes serao mantidas.
"%PYTHON%" manage.py criar_utilizadores_padrao 2>>"%LOGFILE%"
if errorlevel 1 goto users_error

:: ---- Ficheiros estaticos ----
echo.
echo  [5/5] A preparar ficheiros estaticos...
"%PYTHON%" manage.py collectstatic --noinput --clear 2>>"%LOGFILE%"
if errorlevel 1 goto static_error
    echo  [OK] Instalacao completa!

echo.
echo  ===============================================================
echo    INSTALACAO CONCLUIDA COM SUCESSO!
echo  ===============================================================
echo.
echo   O sistema vai abrir no navegador em alguns segundos...
echo.
echo   Endereco local: http://localhost:%PORT%
echo   As palavras-passe foram definidas durante a configuracao.
echo   Para parar o servidor: pressione Ctrl+C
echo.
echo  ===============================================================
echo.

:: Abrir navegador apos 3 segundos
start "" /b cmd /c "timeout /t 3 /nobreak >nul & start "" http://localhost:%PORT%"

:: Iniciar servidor
"%PYTHON%" manage.py runserver 0.0.0.0:%PORT% 2>>"%LOGFILE%"
set "EXIT_CODE=%errorlevel%"
if not "%EXIT_CODE%"=="0" (
    echo.
    echo  [ERRO] O servidor terminou com o codigo %EXIT_CODE%.
    echo  Consulte o ficheiro instalacao.log para ver os detalhes.
    echo.
    pause
)
endlocal & exit /b %EXIT_CODE%

:install_dependencies
set "ATTEMPT=1"
:install_dependencies_attempt
echo.
echo  [INFO] Tentativa %ATTEMPT% de 3. O download pode demorar alguns minutos...
"%PYTHON%" -m pip install -r requirements.txt --prefer-binary --retries 8 --timeout 180 --disable-pip-version-check 2>>"%LOGFILE%"
if not errorlevel 1 exit /b 0
if %ATTEMPT% GEQ 3 exit /b 1
set /a ATTEMPT+=1
echo.
echo  [AVISO] A ligacao foi interrompida. Nova tentativa em 15 segundos...
timeout /t 15 /nobreak >nul
goto install_dependencies_attempt

:try_python
set "CANDIDATE=%~1"
set "CANDIDATE_VERSION="
%CANDIDATE% -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>&1
if errorlevel 1 exit /b 1
for /f "delims=" %%v in ('%CANDIDATE% --version 2^>^&1') do if not defined CANDIDATE_VERSION set "CANDIDATE_VERSION=%%v"
if not defined CANDIDATE_VERSION exit /b 1
set "PYTHON_CMD=%CANDIDATE%"
set "PYVER=%CANDIDATE_VERSION%"
exit /b 0

:python_not_found
echo  [ERRO] Python nao foi encontrado no computador.
echo.
echo  Instale Python 3.11 ou superior em:
echo  https://www.python.org/downloads/
echo  Durante a instalacao, marque "Add Python to PATH".
echo  Depois feche esta janela, abra uma nova e execute o instalador novamente.
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

:port_script_not_found
echo  [ERRO] find_free_port.py nao foi encontrado.
echo  Confirme que o projeto foi extraido completamente.
goto fail

:venv_error
echo  [ERRO] Nao foi possivel criar o ambiente virtual.
echo  Confirme que o Python foi instalado com suporte a ambientes virtuais.
goto fail

:pip_error
echo  [ERRO] O pip nao esta disponivel no ambiente virtual.
echo  Repare a instalacao do Python e execute este instalador novamente.
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

:port_error
echo  [ERRO] Nao foi encontrada uma porta livre entre 8000 e 8999.
echo  Feche algum servidor ou programa local e tente novamente.
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
echo  Os detalhes tecnicos foram guardados em:
echo  %LOGFILE%
pause
endlocal & exit /b 1