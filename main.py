import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

def main():
    load_dotenv()
    
    # Configuración del LLM conectado al proxy interno WindsurfAPI
    windsurf_llm = ChatOpenAI(
        base_url=os.getenv("WINDSURF_API_URL", "http://windsurf-api:3003/v1"),
        api_key=os.getenv("WINDSURF_API_KEY", "default_token"),
        model="claude-3-5-sonnet" # Se puede rotar según la disponibilidad del proxy
    )

    print("Inicializando equipo multiagente de AI Dev Studio...")

    # 1. Agente Planificador (Janus)
    janus_planner = Agent(
        role='Arquitecto de Software y Planificador',
        goal='Planificar la arquitectura técnica y dividir los requerimientos en tareas atómicas.',
        backstory='Eres Janus, el planificador principal del proyecto DataHub. Lees el contexto, consultas las reglas del proyecto y diseñas el paso a paso estructurado.',
        verbose=True,
        allow_delegation=True,
        llm=windsurf_llm
    )

    # 2. Agente Desarrollador Full-Stack
    fullstack_dev = Agent(
        role='Desarrollador Full-Stack Senior',
        goal='Escribir código en Python (FastAPI) y TypeScript (Svelte 5) siguiendo estrictamente las reglas del proyecto.',
        backstory='Eres un desarrollador orientado a detalles que respeta los estándares de arquitectura. Escribes soluciones completas sin omitir secciones.',
        verbose=True,
        allow_delegation=False,
        llm=windsurf_llm
    )

    # 3. Agente QA y Seguridad
    qa_engineer = Agent(
        role='Ingeniero de Calidad y Seguridad (QA)',
        goal='Auditar el código propuesto, buscar vulnerabilidades y verificar el cumplimiento de buenas prácticas.',
        backstory='Eres un auditor analítico. Revisas el código generado por el desarrollador antes de permitir la finalización de la iteración.',
        verbose=True,
        allow_delegation=False,
        llm=windsurf_llm
    )

    # Tarea inicial: Verificación de estado del orquestador
    system_check_task = Task(
        description='Verificar el estado del entorno de orquestación y listar los roles del equipo asignado.',
        expected_output='Un reporte en formato Markdown de máximo 3 párrafos confirmando que el equipo está en línea y detallando sus roles.',
        agent=janus_planner
    )

    # Configuración del flujo de trabajo (Crew)
    ai_crew = Crew(
        agents=[janus_planner, fullstack_dev, qa_engineer],
        tasks=[system_check_task],
        process=Process.sequential,
        verbose=True
    )

    # Ejecución del ciclo
    try:
        result = ai_crew.kickoff()
        
        # Almacenar el reporte en el volumen persistente
        output_dir = "/app/output"
        os.makedirs(output_dir, exist_ok=True)
        
        with open(os.path.join(output_dir, "startup_report.md"), "w", encoding="utf-8") as f:
            # Result puede ser un objeto en versiones recientes de CrewAI, se convierte a string
            f.write(str(result))
            
        print("\nCiclo finalizado. Reporte generado en /app/output/startup_report.md")
    
    except Exception as e:
        print(f"\nError durante la ejecución del equipo multiagente: {str(e)}")

if __name__ == "__main__":
    main()
    