import os
import time
import traceback

def main():
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "frontend_creation_report.md")
    
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("# Estado de AI Dev Studio\nIniciando el contenedor. Cargando herramientas físicas...\n\n")
    except Exception as e:
        pass

    try:
        from dotenv import load_dotenv
        from crewai import Agent, Task, Crew, Process
        from crewai_tools import FileWriterTool
        
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

        frontend_rules = load_skill("frontend-rules.md")
        
        # 1. Preparar el terreno físico para el Frontend en el volumen montado
        workspace_kyc_frontend = "/workspace/datahub/kyc/frontend"
        os.makedirs(workspace_kyc_frontend, exist_ok=True)
        # SvelteKit requiere una estructura específica de carpetas (src/routes)
        os.makedirs(os.path.join(workspace_kyc_frontend, "src", "routes"), exist_ok=True)
        
        # 2. Inicializar la herramienta de escritura con permisos
        file_writer = FileWriterTool()

        with open(report_path, "a", encoding="utf-8") as f:
            f.write("- Herramientas listas. Orquestando al Desarrollador para escribir código Frontend Svelte 5...\n\n")

        fullstack_dev = Agent(
            role='Desarrollador Frontend Senior',
            goal='Escribir archivos de código en TypeScript y Svelte 5 directamente en el disco duro del servidor.',
            backstory=f'Eres un desarrollador Frontend SvelteKit meticuloso. Debes USAR OBLIGATORIAMENTE la herramienta FileWriterTool. Reglas técnicas obligatorias:\n{frontend_rules}',
            verbose=True,
            allow_delegation=False,
            tools=[file_writer]
        )

        coding_task = Task(
            description=(
                'Crea los tres archivos iniciales del frontend para el módulo KyC.\n'
                f'Utiliza tu herramienta `FileWriterTool` para escribir físicamente los archivos en la ruta raíz: {workspace_kyc_frontend}/\n'
                '1. Escribe `svelte.config.js` (en la raíz del frontend) configurando @sveltejs/adapter-node.\n'
                '2. Escribe `src/routes/+layout.ts` configurando obligatoriamente `ssr = false` y `prerender = false`.\n'
                '3. Escribe `src/routes/+page.svelte` creando una vista de bienvenida básica que implemente un estado reactivo usando Svelte 5 Runes (`$state`).\n'
                'Importante: Escribe el código COMPLETO en cada archivo, sin omitir partes ni dejar comentarios de relleno.'
            ),
            expected_output='Un reporte detallando el nombre y ruta de los archivos que se han creado exitosamente en el frontend.',
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
    