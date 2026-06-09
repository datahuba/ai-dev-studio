import os
import time
import traceback

def main():
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "backend_creation_report.md")
    
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Estado de AI Dev Studio\nIniciando el contenedor. Cargando herramientas físicas...\n\n")
    except Exception as e:
        pass

    try:
        from dotenv import load_dotenv
        from crewai import Agent, Task, Crew, Process
        from crewai_tools import FileWriteTool
        
        load_dotenv()
        
        os.environ["OPENAI_API_BASE"] = os.getenv("WINDSURF_API_URL", "http://windsurf-api:3003/v1")
        os.environ["OPENAI_API_KEY"] = os.getenv("WINDSURF_API_KEY", "DataHubAnalytics2025")
        os.environ["OPENAI_MODEL_NAME"] = "openai/gemini-2.5-flash"
        
        def load_skill(file_name):
            path = os.path.join(os.path.dirname(__file__), 'skills', file_name)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""

        backend_rules = load_skill("backend-rules.md")
        
        # 1. Preparar el terreno físico en el volumen montado (/root/datahub en el VPS)
        workspace_kyc_backend = "/workspace/datahub/kyc/backend"
        os.makedirs(workspace_kyc_backend, exist_ok=True)
        
        # 2. Inicializar la herramienta de escritura con permisos sobre la carpeta del proyecto
        file_writer = FileWriteTool()

        with open(report_path, "a", encoding="utf-8") as f:
            f.write("- Herramientas listas. Orquestando al Desarrollador para escribir código real...\n\n")

        fullstack_dev = Agent(
            role='Desarrollador Backend Senior',
            goal='Escribir archivos de código en Python (FastAPI) directamente en el disco duro del servidor.',
            backstory=f'Eres un desarrollador meticuloso. Tienes acceso a herramientas de escritura. Reglas técnicas obligatorias:\n{backend_rules}',
            verbose=True,
            allow_delegation=False,
            tools=[file_writer]
        )

        coding_task = Task(
            description=(
                'Crea los dos archivos iniciales del backend para el módulo KyC basándote en la arquitectura previa.\n'
                f'Utiliza la herramienta `FileWriteTool` para escribir los archivos físicamente en la ruta: {workspace_kyc_backend}/\n'
                '1. Escribe el archivo `main.py` configurando FastAPI, Uvicorn, GZipMiddleware y el lifespan de Beanie.\n'
                '2. Escribe el archivo `models.py` creando un esquema Pydantic v2 básico para el modelo User.\n'
                'Importante: Escribe el código COMPLETO, sin omitir partes ni dejar comentarios de relleno.'
            ),
            expected_output='Un reporte detallando el nombre y ruta de los archivos que se han creado exitosamente en el servidor.',
            agent=fullstack_dev
        )

        ai_crew = Crew(
            agents=[fullstack_dev],
            tasks=[coding_task],
            process=Process.sequential,
            verbose=True
        )
        
        result = ai_crew.kickoff()
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(str(result))
            
        print(f"Ciclo finalizado. Reporte de código generado en {report_path}")

    except Exception as e:
        error_trace = traceback.format_exc()
        with open(report_path, "a", encoding="utf-8") as f:
            f.write("\n## ❌ Error Fatal del Contenedor\n")
            f.write(f"```python\n{error_trace}\n```\n")

    print("Mantenimiento activo para lectura de logs.")
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()
    