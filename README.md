# AI Dev Studio
Equipo multiagente autónomo de desarrollo para el proyecto DataHub.

## Auditoría y Revisión de Resultados

Dado que los agentes operan en un entorno aislado dentro del VPS, las ejecuciones y reportes deben revisarse conectándose al servidor.

### 1. Panel del Proxy de IA (Windsurf API)
Para evadir bloqueos de seguridad de Firebase (Referer) y restricciones de inicio de sesión por correo, la autenticación debe realizarse mediante **Token Directo**.

**Pasos para autenticar el proxy (Estándar Oficial):**
1. Ejecuta el script de túnel en tu máquina local: `.\connect_dashboard.ps1`
2. Ingresa a `http://localhost:3003/dashboard` e inicia sesión con la clave: `DataHubAnalytics2025`.
3. En el panel, dirígete a la sección "Account Login" y baja hasta **"Or paste Auth Token directly"**.
4. Haz clic en "Open windsurf.com for Token".
5. Inicia sesión en la página oficial que se abre, copia el Auth Token devuelto, pégalo en el panel del proxy y haz clic en "Add via Token".

### 2. Ver el razonamiento de los agentes en tiempo real (Logs)
Para observar cómo Janus, el desarrollador y el QA dialogan, delegando tareas y consumiendo la API:
```bash
docker logs -f ai-dev-studio
