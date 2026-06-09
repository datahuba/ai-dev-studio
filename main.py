import os
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

    # 1. Agente Planificador (Janus)
    janus_planner = Agent(
        role='Arquitecto de Software y Planificador',
        goal='Planificar la arquitectura técnica y dividir los requerimientos en tareas atómicas.',
        backstory=f'Eres Janus, el planificador principal del proyecto DataHub. Reglas base obligatorias que debes acatar:\n{backend_rules}\n{frontend_rules}',
        verbose=True,
        allow_delegation=True,
        llm=windsurf_llm
    )

    # 2. Agente Desarrollador Full-Stack
    fullstack_dev = Agent(
        role='Desarrollador Full-Stack Senior',
        goal='Escribir código en Python (FastAPI) y TypeScript (Svelte 5) siguiendo estrictamente las reglas del proyecto.',
        backstory=f'Eres un desarrollador orientado a detalles. Reglas técnicas que rigen tu código:\n{backend_rules}\n{frontend_rules}',
        verbose=True,
        allow_delegation=False,
        llm=windsurf_llm
    )

    # 3. Agente QA y Seguridad
    qa_engineer = Agent(
        role='Ingeniero de Calidad y Seguridad (QA)',
        goal='Auditar el código propuesto, buscar vulnerabilidades y verificar el cumplimiento de las reglas.',
        backstory='Eres un auditor analítico. Revisas el código para asegurar que no se omita código y que cumpla el stack definido.',
        verbose=True,
        allow_delegation=False,
        llm=windsurf_llm
    )

    # Tarea inicial: Generar propuesta de arquitectura respetando el stack
    architecture_task = Task(
        description='Generar un borrador de diseño de arquitectura para el módulo KyC reconociendo explícitamente las reglas de Svelte 5 y FastAPI (Beanie) recibidas en tu contexto.',
        expected_output='Un reporte técnico en Markdown detallando cómo se estructurará la comunicación entre el frontend y backend para el módulo KyC.',
        agent=janus_planner
    )

    # Configuración del flujo de trabajo (Crew)
    ai_crew = Crew(
        agents=[janus_planner, fullstack_dev, qa_engineer],
        tasks=[architecture_task],
        process=Process.sequential,
        verbose=True
    )

    # Ejecución del ciclo
    try:
        result = ai_crew.kickoff()
        
        output_dir = "/app/output"
        os.makedirs(output_dir, exist_ok=True)
        
        with open(os.path.join(output_dir, "architecture_report.md"), "w", encoding="utf-8") as f:
            f.write(str(result))
            
        print("\nCiclo finalizado. Reporte de arquitectura generado en /app/output/architecture_report.md")
    
    except Exception as e:
        print(f"\nError durante la ejecución del equipo multiagente: {str(e)}")

if __name__ == "__main__":
    main()