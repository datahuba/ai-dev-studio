# AI Dev Studio
Equipo multiagente autónomo de desarrollo para el proyecto DataHub.

## Auditoría y Revisión de Resultados

Dado que los agentes operan en un entorno aislado dentro del VPS, las ejecuciones y reportes deben revisarse conectándose al servidor.

### 1. Panel del Proxy de IA (Windsurf API)
Antes de que los agentes puedan generar código, debes asegurarte de proveer cuentas gratuitas al proxy para que este entregue los tokens a la red interna.
- Ingresa desde tu navegador a: `http://<IP_DE_TU_VPS>:3003/dashboard`
- Inicia sesión con la clave de seguridad configurada en las variables de entorno.
- Agrega las sesiones según la documentación del proxy.

### 2. Ver el razonamiento de los agentes en tiempo real (Logs)
Para observar cómo Janus, el desarrollador y el QA dialogan, delegando tareas y consumiendo la API:
```bash
docker logs -f ai-dev-studio