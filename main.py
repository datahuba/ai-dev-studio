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
        model="gemini-2.5-flash", # Usamos Gemini Flash por su velocidad de clasificación
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
        
        # Extraer JSON mediante expresiones regulares por seguridad
        match = re.search(r"\{.*\}", response.content, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception as e:
        print(f"[Enrutador] Error de clasificación: {str(e)}. Usando fallback de seguridad...")
    
    # Fallback conservador si falla el clasificador
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
        from crewai_tools import FileWriterTool, FileReadTool
        
        # 1. Ejecutar clasificación dinámica de la tarea
        print("\n[Enrutador] Analizando requerimiento para optimizar uso de memoria y VPS...")
        config = classify_task(user_prompt)
        print(f"[Enrutador] Análisis de Janus: {config['reasoning']}")
        
        os.environ["OPENAI_API_BASE"] = os.getenv("WINDSURF_API_URL", "http://windsurf-api:3003/v1")
        os.environ["OPENAI_API_KEY"] = os.getenv("WINDSURF_API_KEY", "DataHubAnalytics2025")
        os.environ["OPENAI_MODEL_NAME"] = "openai/gemini-2.5-flash"
        os.environ["CREWAI_TOOLS_ALLOW_UNSAFE_PATHS"] = "true"
        
        # 2. Cargar dinámicamente solo los Skills requeridos (Ahorro de tokens de contexto)
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

        # Inicializar herramientas
        file_writer = FileWriterTool()
        file_reader = FileReadTool()
        
        active_agents = []
        active_tasks = []

        # 3. Ensamblado Dinámico de Agentes (On-Demand)
        # Planificador (Janus)
        if config["requires_planning"]:
            janus_planner = Agent(
                role='Arquitecto de Software y Planificador',
                goal='Analizar requerimientos y diseñar la estructura lógica de los nuevos archivos.',
                backstory=f'Eres Janus. Diseñas soluciones limpias en /workspace/projects/. Reglas aplicables:\n{context_rules}',
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
                backstory=f'Codificador veloz. Creas código real en /workspace/projects/ con FileWriterTool basándote en:\n{context_rules}',
                verbose=True,
                allow_delegation=False,
                tools=[file_reader, file_writer]
            )
            task_dev = Task(
                description=f'Escribe el código fuente completo de los archivos requeridos para satisfacer la instrucción: "{user_prompt}" bajo /workspace/projects/. No uses código truncado.',
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
                backstory='Auditor estricto. Usas FileReadTool para inspeccionar los archivos modificados en /workspace/projects/.',
                verbose=True,
                allow_delegation=False,
                tools=[file_reader]
            )
            task_qa = Task(
                description='Inspecciona los archivos fuente creados en /workspace/projects/ usando FileReadTool. Verifica sintaxis y buenas prácticas.',
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
                backstory='Automatizas entornos. Creas archivos de configuración (Dockerfile, compose, Nginx) en /workspace/projects/ usando FileWriterTool.',
                verbose=True,
                allow_delegation=False,
                tools=[file_writer]
            )
            task_devops = Task(
                description=f'Crea los entornos de infraestructura (Dockerfiles/docker-compose) requeridos para el proyecto en /workspace/projects/ basándote en: "{user_prompt}".',
                expected_output='Confirmación de los archivos de infraestructura creados.',
                agent=devops_engineer
            )
            active_agents.append(devops_engineer)
            active_tasks.append(task_devops)

        # 4. Autocreación Dinámica de Agentes Especialistas (On-The-Fly)
        if config["custom_agent"]["needed"]:
            custom_spec = config["custom_agent"]
            print(f"[Enrutador] 🚀 AUTOCREANDO AGENTE ESPECIALISTA: {custom_spec['role']}")
            
            # Decidir qué herramientas necesita el especialista según el contexto
            spec_tools = [file_reader, file_writer] if config["requires_coding"] else [file_reader]
            
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

        # Validar si hay agentes activos para evitar llamados vacíos
        if not active_agents:
            print("[Enrutador] No se requiere la intervención de ningún agente para esta tarea.")
            return

        # 5. Ejecutar la Crew Optimizada
        print(f"[Enrutador] Iniciando Crew optimizada con {len(active_agents)} agentes activos (Ahorro de recursos activo)...")
        ai_crew = Crew(
            agents=active_agents,
            tasks=active_tasks,
            process=Process.sequential,
            verbose=True
        )

        result = ai_crew.kickoff()
        execution_time = time.time() - start_time

        # 6. Generar Bitácora del Consumo de Recursos
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
    