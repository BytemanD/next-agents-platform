@echo off
chcp 65001 >nul
setlocal

set "SCRIPT=%~nx0"
set "SERVICE=%~1"

if "%SERVICE%"=="" goto :usage

shift

set "EXTRA="
:collect
if "%~1"=="" goto :collected
set "EXTRA=%EXTRA% %~1"
shift
goto :collect
:collected

if /i "%SERVICE%"=="master" goto :master
if /i "%SERVICE%"=="knowledge" goto :knowledge
if /i "%SERVICE%"=="frontend" goto :frontend

echo Unknown service: %SERVICE%
goto :usage

:master
cd /d "%~dp0nap-backend"
uv run uvicorn nap.master.asgi:APP --reload-dir nap --port 18000 %EXTRA%
goto :eof

:knowledge
cd /d "%~dp0nap-backend"
uv run uvicorn nap.knowledge.asgi:APP --reload-dir nap --port 18001 %EXTRA%
goto :eof

:frontend
npm -C "%~dp0nap-frontend" run dev %EXTRA%
goto :eof

:usage
echo Usage: %SCRIPT% {master^|knowledge^|frontend} [extra args...]
echo.
echo   master     启动 Master 服务 (port 18000)
echo   knowledge  启动 Knowledge 服务 (port 18001)
echo   frontend   启动前端开发服务 (vite)
exit /b 1
