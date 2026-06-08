import os
import time
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process

def main():
    load_dotenv()
    
    # 1. Configuración de Variables de Entorno para Intercepción de LLM
    # Redirigimos el tráfico interno de LangChain/CrewAI hacia nuestro proxy Windsurf
    api_base = os.getenv("WINDSURF_API_BASE", "http://windsurf-api:3003/v1")
    os.environ["OPENAI_API_BASE"] = api_base
    os.environ["OPENAI_API_KEY"] = "sk-windsurf-dummy-token"
    # Puedes ajustar el modelo según lo que devuelva tu proxy (ej. gpt-4, claude-3)
    os.environ["OPENAI_MODEL_NAME"] = "gpt-4-turbo" 
    
    print(f"[*] Entorno inicializado. Tráfico LLM redirigido a: {api_base}")
    print("[*] Desplegando equipo de agentes AI Dev Studio...\n")

    # 2. Definición del Agente Planificador
    planner = Agent(
        role='Arquitecto de Software AI',
        goal='Diseñar la estructura base para el equipo autónomo de desarrollo.',
        backstory='Eres un Arquitecto de Software Senior. Tu misión es asegurar que el código generado sea escalable y limpio.',
        verbose=True,
        allow_delegation=False
    )

    # 3. Definición de la Tarea Inicial
    plan_task = Task(
        description='Escribe un breve saludo identificándote como el Arquitecto del proyecto y propón 3 pasos iniciales para analizar el código local de DataHub.',
        expected_output='Un breve esquema en formato Markdown con el saludo y 3 viñetas técnicas.',
        agent=planner
    )

    # 4. Ensamblaje del Equipo (Crew)
    dev_crew = Crew(
        agents=[planner],
        tasks=[plan_task],
        process=Process.sequential,
        verbose=2
    )

    # 5. Ejecución del Flujo
    print("[*] Iniciando ejecución de la tarea. Esperando respuesta del LLM...")
    try:
        result = dev_crew.kickoff()
        print("\n==========================================")
        print("RESULTADO DEL AGENTE:")
        print("==========================================")
        print(result)
    except Exception as e:
        print(f"\n[!] Error durante la ejecución del agente: {e}")
        print("[!] Nota: Verifica que el contenedor 'windsurf-api' esté respondiendo y devolviendo tokens válidos.")

    # 6. Prevención de reinicios en bucle de Docker
    print("\n[*] Ciclo de prueba finalizado. Pausando contenedor...")
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()