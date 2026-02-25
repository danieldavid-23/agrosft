 # Lista de todas las apps
$apps = @("inventario", "cultivos", "clientes", "ventas", "usuarios")

foreach ($app in $apps) {
    Write-Host "Creando estructura para $app..." -ForegroundColor Green
    
    # Ir a la app
    cd apps/$app
    
    # Eliminar archivos por defecto (si existen)
    Remove-Item views.py -Force -ErrorAction SilentlyContinue
    Remove-Item models.py -Force -ErrorAction SilentlyContinue
    Remove-Item tests.py -Force -ErrorAction SilentlyContinue
    
    # Crear carpetas MVC
    $folders = @("models", "views", "controllers", "services", "repositories", "dtos", "forms", "tests")
    
    foreach ($folder in $folders) {
        # Crear carpeta
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        
        # Crear archivo __init__.py dentro de la carpeta
        New-Item "$folder/__init__.py" -ItemType File -Force | Out-Null
    }
    
    # Crear archivo urls.py
    New-Item urls.py -ItemType File -Force | Out-Null
    
    # Volver a apps
    cd ../..
}

Write-Host "Estructura de apps creada exitosamente!" -ForegroundColor Green