import os
import time
import traceback

def main():
    # 1. Asegurar la creación del directorio y archivo ANTES de cualquier lógica pesada
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "architecture_report.md")
    
    try:
        # Escribir una bandera de inicio inmediato para probar que el contenedor funciona
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Estado de AI Dev Studio\nIniciando el contenedor. Cargando librerías...\n\n")
    except Exception as e:
        print(f"Error escribiendo en el disco local: {e}")

    try:
        # 2. Las importaciones de IA están sujetas a fallar por conflictos de versión.
        # Al ponerlas dentro del bloque Try, aseguramos capturar el error.
        from dotenv import load_dotenv
        from crewai import Agent, Task, Crew, Process
        from langchain_openai import ChatOpenAI
        
        load_dotenv()
        
        def load_skill(file_name):
            path = os.path.join(os.path.dirname(__file__), 'skills', file_name)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""

        backend_rules = load_skill("backend-rules.md")
        frontend_rules = load_skill("frontend-rules.md")
        
        # Registrar avance exitoso en el archivo
        with open(report_path, "a", encoding="utf-8") as f:
            f.write("- Dependencias importadas correctamente.\n- Instanciando agentes de IA...\n\n")

        windsurf_llm = ChatOpenAI(
            base_url=os.getenv("WINDSURF_API_URL", "http://windsurf-api:3003/v1"),
            api_key=os.getenv("WINDSURF_API_KEY", "tu_clave_secreta_vps_3003"),
            model="claude-3-5-sonnet"
        )

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
        
        with open(report_path, "a", encoding="utf-8") as f:
            f.write("- Equipo orquestado. Llamando a la API de Windsurf (kickoff)...\n\n")

        result = ai_crew.kickoff()
        
        # Si la comunicación con el LLM tiene éxito, se sobrescribe con el reporte oficial
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(str(result))
            
        print(f"Ciclo finalizado. Reporte generado en {report_path}")

    except Exception as e:
        # Captura cualquier error de importación de Python y lo guarda en el disco
        error_msg = traceback.format_exc()
        with open(report_path, "a", encoding="utf-8") as f:
            f.write("\n## ❌ Error Fatal del Contenedor\n")
            f.write("El script colapsó en tiempo de ejecución. Detalle del Stack Trace:\n")
            f.write(f"```python\n{error_msg}\n```\n")

    # Bucle infinito ligero para evitar reinicios automáticos de Docker y permitir auditar logs
    print("Mantenimiento activo para lectura de logs.")
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
    