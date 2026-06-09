# AI Dev Studio
Equipo multiagente autónomo de desarrollo para el proyecto DataHub.

## Auditoría y Revisión de Resultados

Dado que los agentes operan en un entorno aislado dentro del VPS, las ejecuciones y reportes deben revisarse conectándose al servidor.

### 1. Panel del Proxy de IA (Windsurf API)
Codeium (proveedor de Windsurf) bloquea las peticiones de inicio de sesión mediante OAuth (botones de Google/GitHub) cuando detecta que el referer proviene de un dominio no oficial como `localhost` o una IP externa. Para evadir este bloqueo, se debe utilizar autenticación tradicional (Server-Side).

**Pasos para autenticar el proxy:**
1. Abre una pestaña normal en tu navegador y ve a la página oficial `https://codeium.com` o `https://windsurf.ai`.
2. Regístrate creando una cuenta gratuita nueva usando explícitamente la opción de **Correo y Contraseña** (No utilices los botones de "Continuar con Google/GitHub").
3. Ejecuta el script de túnel en tu máquina local: `.\connect_dashboard.ps1`
4. Ingresa a `http://localhost:3003/dashboard` e inicia sesión en el panel con la clave: `DataHubAnalytics2025`.
5. En el panel, ignora los botones de Google/GitHub y dirígete a la sección **"Email & Password Login"**.
6. Ingresa el correo y la contraseña nativa que acabas de registrar y presiona el botón morado **Login**. 

#### 2. Ver el razonamiento de los agentes en tiempo real (Logs)
Para observar cómo Janus, el desarrollador y el QA dialogan, delegando tareas y consumiendo la API:
```bash
docker logs -f ai-dev-studio