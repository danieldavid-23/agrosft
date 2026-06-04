@echo off
echo ========================================
echo Validando esquema de base de datos...
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
)

REM Ejecutar validacion
echo Ejecutando validacion...
python manage.py shell < scripts\validate_schema.py

echo.
echo ========================================
echo Validacion completada
echo ========================================
pause
