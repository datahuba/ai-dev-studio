import os
import time
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

def load_skill(file_name):
    """Carga el contenido de los archivos markdown de habilidades."""
    path = os.path.join(os.path.dirname(__file__), 'skills', file_name)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def main():
    load_dotenv()
    
    # Preparar el directorio y ruta del archivo de salida
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "architecture_report.md")
    
    # Carga de las reglas de arquitectura desde los archivos físicos
    backend_rules = load_skill("backend-rules.md")
    frontend_rules = load_skill("frontend-rules.md")
    
    # Configuración del LLM conectado al proxy interno WindsurfAPI
    windsurf_llm = ChatOpenAI(
        base_url=os.getenv("WINDSURF_API_URL", "http://windsurf-api:3003/v1"),
        api_key=os.getenv("WINDSURF_API_KEY", "tu_clave_secreta_vps_3003"),
        model="claude-3-5-sonnet"
    )

    print("Inicializando equipo multiagente con inyección de contexto DataHub...")

    janus_planner = Agent(
        role='Arquitecto de Software y Planificador',
        goal='Planificar la arquitectura técnica y dividir los requerimientos en tareas atómicas.',
        backstory=f'Eres Janus, el planificador principal del proyecto DataHub. Reglas base obligatorias que debes acatar:\n{backend_rules}\n{frontend_rules}',
        verbose=True,
        allow_delegation=True,
        llm=windsurf_llm
    )

    fullstack_dev = Agent(
        role='Desarrollador Full-Stack Senior',
        goal='Escribir código en Python (FastAPI) y TypeScript (Svelte 5) siguiendo estrictamente las reglas del proyecto.',
        backstory=f'Eres un desarrollador orientado a detalles. Reglas técnicas que rigen tu código:\n{backend_rules}\n{frontend_rules}',
        verbose=True,
        allow_delegation=False,
        llm=windsurf_llm
    )

    qa_engineer = Agent(
        role='Ingeniero de Calidad y Seguridad (QA)',
        goal='Auditar el código propuesto, buscar vulnerabilidades y verificar el cumplimiento de las reglas.',
        backstory='Eres un auditor analítico. Revisas el código para asegurar que no se omita código y que cumpla el stack definido.',
        verbose=True,
        allow_delegation=False,
        llm=windsurf_llm
    )

    architecture_task = Task(
        description='Generar un borrador de diseño de arquitectura para el módulo KyC reconociendo explícitamente las reglas de Svelte 5 y FastAPI (Beanie) recibidas en tu contexto.',
        expected_output='Un reporte técnico en Markdown detallando cómo se estructurará la comunicación entre el frontend y backend para el módulo KyC.',
        agent=janus_planner
    )

    ai_crew = Crew(
        agents=[janus_planner, fullstack_dev, qa_engineer],
        tasks=[architecture_task],
        process=Process.sequential,
        verbose=True
    )

    try:
        print("Iniciando el sprint de los agentes (kickoff)...")
        result = ai_crew.kickoff()
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(str(result))
            
        print(f"\nCiclo finalizado. Reporte de arquitectura generado en {report_path}")
    
    except Exception as e:
        # Documentar el error en el archivo para que sea visible vía SSH
        error_message = (
            "# Error en la Ejecución de los Agentes\n\n"
            "**Detalle del fallo técnico:**\n"
            f"```text\n{str(e)}\n```\n\n"
            "**Diagnóstico probable:**\n"
            "El proxy `windsurf-api` rechazó la conexión o devolvió un error (ej. 401 Unauthorized). "
            "Para resolver esto, debes ingresar a `http://<IP_DE_TU_VPS>:3003` desde tu navegador, "
            "vincular una sesión gratuita de Windsurf/Codeium en el panel y reiniciar este contenedor."
        )
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(error_message)
            
        print(f"\nEjecución fallida. El error ha sido documentado en {report_path}")

    # Evitar el reinicio en bucle de Docker Compose manteniendo el proceso en suspensión
    print("\nManteniendo el contenedor activo en segundo plano para auditoría de logs...")
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()