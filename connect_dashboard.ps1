# connect_dashboard.ps1
Write-Host "====================================================="
Write-Host "  Iniciando Túnel Seguro hacia el Proxy WindsurfAPI"
Write-Host "====================================================="
Write-Host "Al solicitarlo, ingresa la contraseña de tu VPS."
Write-Host "Mantén esta ventana abierta para mantener la conexión."
Write-Host "-----------------------------------------------------"
Write-Host "Una vez conectado, abre en tu navegador web:"
Write-Host "--> http://localhost:3003/dashboard"
Write-Host "-----------------------------------------------------"

# Crea un túnel SSH desde el puerto 3003 local hacia el puerto 3003 del VPS
ssh -L 3003:localhost:3003 root@84.247.181.176