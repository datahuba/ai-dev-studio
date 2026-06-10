import os
import sys
import time
import json
import re
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

def classify_task(user_prompt):
    """Llama a la API de forma ligera para clasificar la tarea y decidir qué agentes se necesitan."""
    from langchain_openai import ChatOpenAI
    
    classifier_llm = ChatOpenAI(
        base_url=os.getenv("WINDSURF_API_URL", "http://windsurf-api:3003/v1"),
        api_key=os.getenv("WINDSURF_API_KEY", "DataHubAnalytics2025"),
        model="gemini-2.5-flash",
        temperature=0.0
    )
    
    system_prompt = (
        "Eres el Enrutador Inteligente de AI Dev Studio. Tu tarea es analizar la instrucción del usuario "
        "y decidir de forma óptima qué agentes y habilidades se necesitan. Evita el desperdicio de recursos.\n\n"
        "Debes responder ESTRICTAMENTE en formato JSON válido. No agregues explicaciones fuera del JSON.\n\n"
        "Estructura JSON requerida:\n"
        "{\n"
        '  "reasoning": "Breve explicación de la estrategia de optimización.",\n'
        '  "requires_planning": true/false (solo si es un proyecto nuevo complejo desde cero),\n'
        '  "requires_coding": true/false (si implica escribir o modificar archivos de código),\n'
        '  "requires_qa": true/false (solo si el código modificado requiere auditoría de seguridad o sintaxis),\n'
        '  "requires_devops": true/false (solo si implica Docker, compose, bash o scripts de sistema),\n'
        '  "skills_needed": ["frontend", "backend"] (lista de habilidades; vacía si no aplica),\n'
        '  "custom_agent": {\n'
        '    "needed": true/false (solo si la tarea requiere un especialista muy específico no cubierto por los roles estándar),\n'
        '    "role": "Nombre del rol especialista",\n'
        '    "goal": "Meta específica del especialista",\n'
        '    "backstory": "Historia de fondo y herramientas que usará"\n'
        "  }\n"
        "}"
    )
    
    try:
        response = classifier_llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ])
        
        match = re.search(r"\{.*\}", response.content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        print(f"[Enrutador] Error de clasificación: {str(e)}. Usando fallback de seguridad...")
    
    return {
        "reasoning": "Fallback por fallo en el clasificador.",
        "requires_planning": True,
        "requires_coding": True,
        "requires_qa": True,
        "requires_devops": True,
        "skills_needed": ["frontend", "backend"],
        "custom_agent": {"needed": False, "role": "", "goal": "", "backstory": ""}
    }

def run_sprint(user_prompt):
    output_dir = "/app/output"
    os.makedirs(output_dir, exist_ok=True)
    bitacora_path = os.path.join(output_dir, "bitacora.md")
    start_time = time.time()

    try:
        from crewai import Agent, Task, Crew, Process
        from crewai.tools import tool
        
        # 1. Ejecutar clasificación dinámica de la tarea
        print("\n[Enrutador] Analizando requerimiento para optimizar uso de memoria y VPS...")
        config = classify_task(user_prompt)
        print(f"[Enrutador] Análisis de Janus: {config['reasoning']}")
        
        os.environ["OPENAI_API_BASE"] = os.getenv("WINDSURF_API_URL", "http://windsurf-api:3003/v1")
        os.environ["OPENAI_API_KEY"] = os.getenv("WINDSURF_API_KEY", "DataHubAnalytics2025")
        os.environ["OPENAI_MODEL_NAME"] = "openai/gemini-2.5-flash"
        
        # Cargar dinámicamente solo los Skills requeridos
        def load_skill(file_name):
            path = os.path.join(os.path.dirname(__file__), 'skills', file_name)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""

        context_rules = ""
        if "backend" in config["skills_needed"]:
            context_rules += "\n" + load_skill("backend-rules.md")
        if "frontend" in config["skills_needed"]:
            context_rules += "\n" + load_skill("frontend-rules.md")

        # Asegurar el directorio sandbox
        os.makedirs("/workspace/projects", exist_ok=True)
        
        # 2. DEFINICIÓN DE HERRAMIENTAS PERSONALIZADAS (CUSTOM TOOLS) CON RUTAS SEGURAS
        @tool("write_file")
        def write_file(filename: str, content: str, subdir: str = "") -> str:
            """Escribe contenido directamente en un archivo dentro del directorio sandbox (/workspace/projects).
            Args:
                filename: Nombre del archivo a crear (ej: 'main.py' o 'docker-compose.yml').
                content: El contenido de texto completo que se escribirá en el archivo.
                subdir: Subcarpeta opcional dentro del sandbox (ej: 'backend' o 'frontend').
            """
            base_dir = "/workspace/projects"
            target_dir = os.path.join(base_dir, subdir) if subdir else base_dir
            os.makedirs(target_dir, exist_ok=True)
            filepath = os.path.join(target_dir, filename)
            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                return f"Content successfully written to {filepath}"
            except Exception as e:
                return f"Error writing file: {str(e)}"

        @tool("read_file")
        def read_file(filename: str, subdir: str = "") -> str:
            """Lee el contenido de un archivo en el directorio sandbox o en la carpeta de referencia de DataHub.
            Args:
                filename: Nombre del archivo a leer.
                subdir: Subcarpeta opcional de contexto (ej: 'kyc/backend' o 'frontend').
            """
            # Primero intenta leer del sandbox de proyectos
            base_dir = "/workspace/projects"
            target_dir = os.path.join(base_dir, subdir) if subdir else base_dir
            filepath = os.path.join(target_dir, filename)
            
            # Si no existe, intenta leer de DataHub (Contexto protegido de Solo Lectura)
            if not os.path.exists(filepath):
                base_dir = "/workspace/datahub"
                target_dir = os.path.join(base_dir, subdir) if subdir else base_dir
                filepath = os.path.join(target_dir, filename)
                
            try:
                if os.path.exists(filepath):
                    with open(filepath, "r", encoding="utf-8") as f:
                        return f.read()
                return f"File not found: {filepath}"
            except Exception as e:
                return f"Error reading file: {str(e)}"
        
        active_agents = []
        active_tasks = []

        # 3. Ensamblado Dinámico de Agentes e instrucciones adaptativas (On-Demand)
        # Planificador (Janus)
        if config["requires_planning"]:
            janus_planner = Agent(
                role='Arquitecto de Software y Planificador',
                goal='Analizar requerimientos y diseñar la estructura lógica de los nuevos archivos.',
                backstory=f'Eres Janus. Diseñas soluciones limpias en la raíz del sandbox. Reglas aplicables:\n{context_rules}',
                verbose=True,
                allow_delegation=True
            )
            task_plan = Task(
                description=f'Diseña la estructura de carpetas y archivos necesarios bajo /workspace/projects/ para: "{user_prompt}".',
                expected_output='Plan detallado del nuevo proyecto.',
                agent=janus_planner
            )
            active_agents.append(janus_planner)
            active_tasks.append(task_plan)

        # Coder (Desarrollador)
        if config["requires_coding"]:
            fullstack_dev = Agent(
                role='Desarrollador Full-Stack Senior',
                goal='Escribir código completo y limpio basándose en planos técnicos.',
                backstory='Eres un codificador veloz y preciso. Lees con read_file y creas código real en /workspace/projects/ con write_file.',
                verbose=True,
                allow_delegation=False,
                tools=[read_file, write_file]
            )
            
            if config["requires_planning"]:
                dev_description = (
                    'Sigue el plan de desarrollo diseñado por Janus.\n'
                    'Crea y escribe el código fuente de los archivos requeridos bajo la carpeta de la herramienta.\n'
                    'Asegúrate de que el código esté 100% completo.'
                )
            else:
                dev_description = (
                    f'Analiza directamente el requerimiento del usuario: "{user_prompt}".\n'
                    'Crea y escribe el código fuente de los archivos necesarios utilizando write_file.\n'
                    'Escribe directamente en el directorio asignado por la herramienta.'
                )

            task_dev = Task(
                description=dev_description,
                expected_output='Resumen de archivos de código creados en el disco duro.',
                agent=fullstack_dev
            )
            active_agents.append(fullstack_dev)
            active_tasks.append(task_dev)

        # Auditor de QA
        if config["requires_qa"]:
            qa_engineer = Agent(
                role='Ingeniero de Calidad y Seguridad (QA)',
                goal='Auditar el código producido, validar la sintaxis y asegurar que no haya omisiones.',
                backstory='Auditor estricto. Usas read_file para inspeccionar los archivos modificados en /workspace/projects/.',
                verbose=True,
                allow_delegation=False,
                tools=[read_file]
            )
            task_qa = Task(
                description='Inspecciona los archivos fuente creados bajo el sandbox usando read_file. Verifica sintaxis y buenas prácticas.',
                expected_output='Vedicto de QA indicando si el código es seguro y completo.',
                agent=qa_engineer
            )
            active_agents.append(qa_engineer)
            active_tasks.append(task_qa)

        # Ingeniero DevOps
        if config["requires_devops"]:
            devops_engineer = Agent(
                role='Ingeniero DevOps Senior',
                goal='Configurar el entorno de ejecución, Dockerfiles y compose para los nuevos proyectos.',
                backstory='Automatizas entornos. Creas archivos de configuración (Dockerfile, compose, Nginx) usando la herramienta write_file.',
                verbose=True,
                allow_delegation=False,
                tools=[write_file]
            )
            task_devops = Task(
                description=f'Crea los entornos de infraestructura (Dockerfiles/docker-compose) requeridos para el proyecto bajo la ruta de la herramienta basándote en: "{user_prompt}".',
                expected_output='Confirmación de los archivos de infraestructura creados.',
                agent=devops_engineer
            )
            active_agents.append(devops_engineer)
            active_tasks.append(task_devops)

        # Autocreación Dinámica de Agentes Especialistas (On-The-Fly)
        if config["custom_agent"]["needed"]:
            custom_spec = config["custom_agent"]
            print(f"[Enrutador] 🚀 AUTOCREANDO AGENTE ESPECIALISTA: {custom_spec['role']}")
            
            spec_tools = [read_file, write_file] if config["requires_coding"] else [read_file]
            
            specialist_agent = Agent(
                role=custom_spec["role"],
                goal=custom_spec["goal"],
                backstory=custom_spec["backstory"],
                verbose=True,
                allow_delegation=False,
                tools=spec_tools
            )
            task_specialist = Task(
                description=f'Ejecuta la tarea experta requerida para: "{user_prompt}" aplicando tu rol especializado.',
                expected_output=f'Resultado experto generado por el agente {custom_spec["role"]}.',
                agent=specialist_agent
            )
            active_agents.append(specialist_agent)
            active_tasks.append(task_specialist)

        if not active_agents:
            print("[Enrutador] No se requiere la intervención de ningún agente para esta tarea.")
            return

        # Ejecutar la Crew Optimizada
        print(f"[Enrutador] Iniciando Crew optimizada con {len(active_agents)} agentes activos (Ahorro de recursos activo)...")
        ai_crew = Crew(
            agents=active_agents,
            tasks=active_tasks,
            process=Process.sequential,
            verbose=True
        )

        result = ai_crew.kickoff()
        execution_time = time.time() - start_time

        # Generar Bitácora del Consumo de Recursos
        bitacora_content = (
            "# 📋 BÍTÁCORA DE EJECUCIÓN Y CONSUMO DE RECURSOS\n\n"
            f"**Instrucción Procesada:** `{user_prompt}`\n"
            f"**Tiempo de Ejecución:** `{execution_time:.2f} segundos`\n"
            f"**Estrategia de Enrutamiento:** {config['reasoning']}\n\n"
            "### 🤖 Agentes Activados para esta Tarea:\n"
        )
        for agent in active_agents:
            bitacora_content += f"- **{agent.role}** (Objetivo: {agent.goal})\n"
            
        bitacora_content += f"\n### 📊 Optimización del VPS:\n"
        agentes_ahorrados = 4 - (len(active_agents) - (1 if config["custom_agent"]["needed"] else 0))
        bitacora_content += (
            f"- Agentes del Core omitidos (Ahorro de RAM/Tokens): `{max(0, agentes_ahorrados)} de 4`\n"
            f"- Agentes especialistas autocreados: `{1 if config['custom_agent']['needed'] else 0}`\n"
            f"- Habilidades (Skills) inyectadas en contexto: `{', '.join(config['skills_needed']) if config['skills_needed'] else 'Ninguna (Genérico)'}`\n\n"
            f"### 📝 Resultado del Sprint:\n\n{str(result)}"
        )

        with open(bitacora_path, "w", encoding="utf-8") as f:
            f.write(bitacora_content)
            
        print(f"\n[AI Dev Studio] Sprint finalizado. Bitácora de recursos guardada en {bitacora_path}")

    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"\n=== ❌ ERROR EN SPRINT ===\n{error_trace}\n==========================")

def main():
    load_dotenv()
    
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
    