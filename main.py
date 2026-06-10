import os
import sys
import time
import traceback
from dotenv import load_dotenv

def list_existing_projects():
    """Escanea el directorio sandbox y lista los proyectos creados por la IA."""
    projects_dir = "/workspace/projects"
    print("📁 Directorio de Proyectos Sandbox (/root/ai-dev-projects/):")
    if os.path.exists(projects_dir):
        try:
            projects = [d for d in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, d))]
            if projects:
                for p in projects:
                    print(f"  └── 📂 {p}")
            else:
                print("  (Aún no hay proyectos creados en el Sandbox)")
        except Exception as e:
            print(f"  (No se pudo escanear el directorio: {str(e)})")
    else:
        print("  (Directorio Sandbox no inicializado)")
    print("--------------------------------------------------------")

def run_sprint(user_prompt):
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "sprint_report.md")

    try:
        from crewai import Agent, Task, Crew, Process
        from crewai_tools import FileWriterTool, FileReadTool
        
        os.environ["OPENAI_API_BASE"] = os.getenv("WINDSURF_API_URL", "http://windsurf-api:3003/v1")
        os.environ["OPENAI_API_KEY"] = os.getenv("WINDSURF_API_KEY", "DataHubAnalytics2025")
        os.environ["OPENAI_MODEL_NAME"] = "openai/gemini-2.5-flash"
        os.environ["CREWAI_TOOLS_ALLOW_UNSAFE_PATHS"] = "true"
        
        def load_skill(file_name):
            path = os.path.join(os.path.dirname(__file__), 'skills', file_name)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
                return ""

        backend_rules = load_skill("backend-rules.md")
        frontend_rules = load_skill("frontend-rules.md")

        # Asegurar el directorio sandbox de nuevos proyectos
        os.makedirs("/workspace/projects", exist_ok=True)
        
        # Inicializar herramientas
        file_writer = FileWriterTool()
        file_reader = FileReadTool()

        print("\n[AI Dev Studio] Orquestando equipo avanzado de agentes...")

        # 1. Agente Janus (Planificador / Arquitecto)
        janus_planner = Agent(
            role='Arquitecto de Software y Planificador',
            goal='Analizar requerimientos de nuevos proyectos y diseñar el paso a paso detallado de archivos.',
            backstory=f'Eres Janus. Diseñas soluciones limpias desde cero en la carpeta /workspace/projects/. Tienes de referencia las reglas de DataHub:\n{backend_rules}\n{frontend_rules}',
            verbose=True,
            allow_delegation=True
        )

        # 2. Agente Desarrollador (Coder)
        fullstack_dev = Agent(
            role='Desarrollador Full-Stack Senior',
            goal='Escribir código completo, funcional y limpio basándose en planos técnicos.',
            backstory='Eres un codificador veloz y preciso. Lees archivos con FileReadTool y creas código real en /workspace/projects/ con FileWriterTool.',
            verbose=True,
            allow_delegation=False,
            tools=[file_reader, file_writer]
        )

        # 3. Agente QA (Auditor de Calidad y Seguridad)
        qa_engineer = Agent(
            role='Ingeniero de Calidad y Seguridad (QA)',
            goal='Auditar el código producido, validar la sintaxis y asegurar que no haya omisiones.',
            backstory='No dejas pasar un solo error. Usas FileReadTool para inspeccionar los archivos modificados en /workspace/projects/ y rechazas el trabajo si está incompleto.',
            verbose=True,
            allow_delegation=False,
            tools=[file_reader]
        )

        # 4. Agente DevOps (Ingeniero de Sistemas)
        devops_engineer = Agent(
            role='Ingeniero DevOps Senior',
            goal='Configurar el entorno de ejecución, Dockerfiles, docker-compose y scripts para los nuevos proyectos.',
            backstory='Automatizas entornos. Creas archivos de configuración (Dockerfile, compose, Nginx) en /workspace/projects/ usando la herramienta FileWriterTool.',
            verbose=True,
            allow_delegation=False,
            tools=[file_writer]
        )

        # Configuración de Tareas Secuenciales
        task_plan = Task(
            description=f'Analiza el nuevo requerimiento del usuario: "{user_prompt}". Diseña la estructura de carpetas y archivos necesarios bajo /workspace/projects/ de forma modular.',
            expected_output='Plan detallado del nuevo proyecto y lista de archivos a crear.',
            agent=janus_planner
        )

        task_dev = Task(
            description='Sigue el plan de Janus. Crea y escribe el código fuente de los archivos de lógica (backend/frontend) usando FileWriterTool bajo la ruta /workspace/projects/. Asegúrate de que el código esté 100% completo.',
            expected_output='Resumen de archivos de código creados en el disco duro.',
            agent=fullstack_dev
        )

        task_qa = Task(
            description='Inspecciona los archivos fuente creados en /workspace/projects/ usando FileReadTool. Verifica que no existan errores de sintaxis y que se cumplan las buenas prácticas del framework.',
            expected_output='Vedicto de QA indicando si el código es seguro y completo.',
            agent=qa_engineer
        )

        task_devops = Task(
            description='Crea el entorno de ejecución para el nuevo proyecto en /workspace/projects/ (un Dockerfile y/o un docker-compose.yml básico) usando FileWriterTool.',
            expected_output='Confirmación de los archivos de infraestructura creados.',
            agent=devops_engineer
        )

        ai_crew = Crew(
            agents=[janus_planner, fullstack_dev, qa_engineer, devops_engineer],
            tasks=[task_plan, task_dev, task_qa, task_devops],
            process=Process.sequential,
            verbose=True
        )

        print("[AI Dev Studio] Iniciando Sprint...")
        result = ai_crew.kickoff()

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Reporte de Sprint\n**Instrucción:** {user_prompt}\n\n## Resultado del Equipo\n{str(result)}")

        print(f"\n[AI Dev Studio] ¡Sprint finalizado con éxito! Reporte escrito en {report_path}")

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"\n=== ❌ ERROR EN SPRINT ===\n{error_trace}\n==========================")

def main():
    load_dotenv()
    
    # Encabezado del modo interactivo CLI
    print("\n========================================================")
    print("   🤖 BIENVENIDO AL PANEL INTERACTIVO DE AI DEV STUDIO  ")
    print("========================================================")
    list_existing_projects()
    
    try:
        user_prompt = input("\nIngrese su requerimiento o instrucción: ")
        if user_prompt.strip():
            run_sprint(user_prompt)
        else:
            print("[AI Dev Studio] Instrucción vacía. Cancelando...")
    except KeyboardInterrupt:
        print("\n[AI Dev Studio] Sesión cancelada por el usuario.")

if __name__ == "__main__":
    main()
    