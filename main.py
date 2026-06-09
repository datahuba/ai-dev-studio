import os
import time
import traceback

def main():
    output_dir = "/app/output"
    memory_dir = "/app/memory"
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(memory_dir, exist_ok=True)
    
    report_path = os.path.join(output_dir, "sprint_report.md")
    prompt_path = os.path.join(memory_dir, "prompt.txt")
    
    if not os.path.exists(prompt_path):
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write("Instrucción para la IA: Lee el archivo /workspace/datahub/kyc/frontend/src/routes/+page.svelte y agrégale un botón de color rojo que reinicie la variable 'name' a su estado original.")

    try:
        from dotenv import load_dotenv
        from crewai import Agent, Task, Crew, Process
        from crewai_tools import FileWriterTool, FileReadTool
        
        load_dotenv()
        
        os.environ["OPENAI_API_BASE"] = os.getenv("WINDSURF_API_URL", "http://windsurf-api:3003/v1")
        os.environ["OPENAI_API_KEY"] = os.getenv("WINDSURF_API_KEY", "DataHubAnalytics2025")
        os.environ["OPENAI_MODEL_NAME"] = "openai/gemini-2.5-flash"
        
        # Autorizar explícitamente a CrewAI para que lea/escriba fuera de la carpeta /app
        os.environ["CREWAI_TOOLS_ALLOW_UNSAFE_PATHS"] = "true"
        
        def load_skill(file_name):
            path = os.path.join(os.path.dirname(__file__), 'skills', file_name)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""

        backend_rules = load_skill("backend-rules.md")
        frontend_rules = load_skill("frontend-rules.md")
        
        with open(prompt_path, "r", encoding="utf-8") as f:
            user_prompt = f.read().strip()
            
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# AI Dev Studio - Nuevo Sprint\n**Instrucción recibida:** {user_prompt}\n\n")

        file_writer = FileWriterTool()
        file_reader = FileReadTool()

        planner = Agent(
            role='Arquitecto de Software y Planificador',
            goal='Analizar la solicitud del usuario y definir qué archivos del sistema deben modificarse.',
            backstory=f'Eres Janus. Tu labor es guiar al equipo respetando estas reglas:\n{backend_rules}\n{frontend_rules}',
            verbose=True,
            allow_delegation=False
        )

        developer = Agent(
            role='Desarrollador Full-Stack Senior',
            goal='Leer el código existente y escribir las modificaciones requeridas en el disco duro.',
            backstory='Tienes acceso al sistema de archivos. Usa FileReadTool para entender el código actual y FileWriterTool para aplicar cambios. NUNCA resumas código, escríbelo completo.',
            verbose=True,
            allow_delegation=False,
            tools=[file_reader, file_writer]
        )

        qa_engineer = Agent(
            role='Ingeniero de Calidad y Seguridad (QA)',
            goal='Verificar que el código escrito por el desarrollador funcione y cumpla con las reglas del framework.',
            backstory='Eres el filtro final. Usas FileReadTool para leer lo que el desarrollador escribió y garantizas que cumpla con Svelte 5 y FastAPI.',
            verbose=True,
            allow_delegation=False,
            tools=[file_reader]
        )

        plan_task = Task(
            description=f'Analiza la siguiente instrucción del usuario: "{user_prompt}". Crea un plan paso a paso indicando qué rutas absolutas en /workspace/datahub/ deben leerse y modificarse.',
            expected_output='Un plan de acción con la lista de archivos a afectar.',
            agent=planner
        )

        dev_task = Task(
            description='Ejecuta el plan del Planificador. 1) Usa FileReadTool para leer los archivos necesarios. 2) Usa FileWriterTool para escribir el nuevo código. IMPORTANTE: Usa rutas absolutas (/workspace/datahub/...).',
            expected_output='Confirmación de los archivos escritos exitosamente.',
            agent=developer
        )

        qa_task = Task(
            description='Usa FileReadTool para leer los archivos que el desarrollador acaba de modificar en este sprint. Verifica que no haya código truncado y redacta el reporte final.',
            expected_output='Un reporte de auditoría en Markdown indicando si el código implementado es apto para producción.',
            agent=qa_engineer
        )

        ai_crew = Crew(
            agents=[planner, developer, qa_engineer],
            tasks=[plan_task, dev_task, qa_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = ai_crew.kickoff()
        
        with open(report_path, "a", encoding="utf-8") as f:
            f.write(str(result))
            
        print(f"Ciclo finalizado. Reporte de código generado en {report_path}")

    except Exception as e:
        error_trace = traceback.format_exc()
        print("\n=== ❌ ERROR FATAL DETECTADO ===")
        print(error_trace)
        print("================================\n")
        
        with open(report_path, "a", encoding="utf-8") as f:
            f.write("\n## ❌ Error Fatal del Contenedor\n")
            f.write(f"```python\n{error_trace}\n```\n")

    print("Mantenimiento activo para lectura de logs.")
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
    