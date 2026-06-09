import os
import time
import traceback

def main():
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "architecture_report.md")
    
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Estado de AI Dev Studio\nIniciando el contenedor. Cargando librerías...\n\n")
    except Exception as e:
        print(f"Error escribiendo en el disco local: {e}")

    try:
        from dotenv import load_dotenv
        from crewai import Agent, Task, Crew, Process
        
        load_dotenv()
        
        os.environ["OPENAI_API_BASE"] = os.getenv("WINDSURF_API_URL", "http://windsurf-api:3003/v1")
        os.environ["OPENAI_API_KEY"] = os.getenv("WINDSURF_API_KEY", "DataHubAnalytics2025")
        
        # Corrección: El prefijo "openai/" fuerza a CrewAI a utilizar el protocolo HTTP estándar
        # y enviar la petición a nuestro proxy, evitando que intente cargar la librería nativa de Google.
        os.environ["OPENAI_MODEL_NAME"] = "openai/gemini-2.5-flash"
        
        def load_skill(file_name):
            path = os.path.join(os.path.dirname(__file__), 'skills', file_name)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""

        backend_rules = load_skill("backend-rules.md")
        frontend_rules = load_skill("frontend-rules.md")
        
        with open(report_path, "a", encoding="utf-8") as f:
            f.write("- Dependencias cargadas. Orquestando equipo de IA...\n\n")

        janus_planner = Agent(
            role='Arquitecto de Software y Planificador',
            goal='Planificar la arquitectura técnica y dividir los requerimientos en tareas atómicas.',
            backstory=f'Eres Janus, el planificador principal del proyecto DataHub. Reglas base obligatorias que debes acatar:\n{backend_rules}\n{frontend_rules}',
            verbose=True,
            allow_delegation=True
        )

        fullstack_dev = Agent(
            role='Desarrollador Full-Stack Senior',
            goal='Escribir código en Python (FastAPI) y TypeScript (Svelte 5) siguiendo estrictamente las reglas del proyecto.',
            backstory=f'Eres un desarrollador orientado a detalles. Reglas técnicas que rigen tu código:\n{backend_rules}\n{frontend_rules}',
            verbose=True,
            allow_delegation=False
        )

        qa_engineer = Agent(
            role='Ingeniero de Calidad y Seguridad (QA)',
            goal='Auditar el código propuesto, buscar vulnerabilidades y verificar el cumplimiento de las reglas.',
            backstory='Eres un auditor analítico. Revisas el código para asegurar que no se omita código y que cumpla el stack definido.',
            verbose=True,
            allow_delegation=False
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
        
        with open(report_path, "a", encoding="utf-8") as f:
            f.write(f"- Equipo orquestado. Llamando al proxy (Modelo: {os.environ['OPENAI_MODEL_NAME']})...\n\n")

        result = ai_crew.kickoff()
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(str(result))
            
        print(f"Ciclo finalizado. Reporte generado en {report_path}")

    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        
        if "No active accounts" in error_msg or "503" in error_msg:
            mensaje_amigable = (
                "# ⚠️ Configuración Pendiente: Proxy Sin Cuentas\n\n"
                "El orquestador logró conectarse al proxy `windsurf-api`, pero este respondió con un error `503 No active accounts`.\n\n"
                "**Pasos para resolverlo:**\n"
                "1. Abre tu navegador web e ingresa a `http://<IP_DE_TU_VPS>:3003/dashboard`\n"
                "2. Inicia sesión usando la clave: `DataHubAnalytics2025`.\n"
                "3. Añade al menos una cuenta gratuita.\n"
                "4. Reinicia este contenedor en tu terminal SSH: `docker restart ai-dev-studio`\n"
            )
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(mensaje_amigable)
        else:
            with open(report_path, "a", encoding="utf-8") as f:
                f.write("\n## ❌ Error Fatal del Contenedor\n")
                f.write("El script colapsó en tiempo de ejecución. Detalle del Stack Trace:\n")
                f.write(f"```python\n{error_trace}\n```\n")

    print("Mantenimiento activo para lectura de logs.")
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
    