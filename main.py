import os
import time
import traceback
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

def main():
    load_dotenv()
    
    api_base = os.getenv("WINDSURF_API_BASE", "http://windsurf-api:3003/v1")
    print(f"[*] Entorno inicializado. Configurando LLM hacia: {api_base}")
    
    # Instanciación explícita del LLM para evitar fallos de lectura de variables de entorno
    custom_llm = ChatOpenAI(
        api_key="sk-windsurf-dummy-token",
        base_url=api_base,
        model_name="gpt-4-turbo"
    )

    print("[*] Desplegando equipo de agentes AI Dev Studio...\n")

    # 1. Agentes
    planner = Agent(
        role='Arquitecto de Software AI',
        goal='Diseñar la estructura base y los pasos a seguir para el desarrollo.',
        backstory='Eres un Arquitecto de Software Senior encargado de guiar al equipo.',
        verbose=True,
        allow_delegation=False,
        llm=custom_llm
    )

    developer = Agent(
        role='Desarrollador Full-Stack',
        goal='Escribir el código en FastAPI y SvelteKit siguiendo el plan del Arquitecto.',
        backstory='Eres un desarrollador experto en Python y TypeScript.',
        verbose=True,
        allow_delegation=False,
        llm=custom_llm
    )

    qa_engineer = Agent(
        role='Ingeniero de QA',
        goal='Revisar el código generado, buscar bugs y asegurar la calidad.',
        backstory='Eres un auditor de código riguroso que no deja pasar ninguna falla.',
        verbose=True,
        allow_delegation=False,
        llm=custom_llm
    )

    # 2. Tareas Secuenciales
    plan_task = Task(
        description='Analizar el requerimiento inicial y proponer un plan de acción de 3 pasos.',
        expected_output='Un plan en Markdown con 3 viñetas.',
        agent=planner
    )

    code_task = Task(
        description='Basado en el plan del Arquitecto, escribe el código necesario.',
        expected_output='Código fuente implementado.',
        agent=developer
    )

    qa_task = Task(
        description='Revisa el código entregado por el desarrollador y emite un veredicto.',
        expected_output='Un reporte de QA aprobando o rechazando el código.',
        agent=qa_engineer
    )

    # 3. Ensamblaje del Equipo (Crew)
    dev_crew = Crew(
        agents=[planner, developer, qa_engineer],
        tasks=[plan_task, code_task, qa_task],
        process=Process.sequential,
        verbose=2
    )

    # 4. Ejecución
    print("[*] Iniciando flujo secuencial del equipo. Procesando...")
    try:
        result = dev_crew.kickoff()
        print("\n==========================================")
        print("RESULTADO FINAL DEL EQUIPO (Reporte de QA):")
        print("==========================================")
        print(result)
    except Exception as e:
        print(f"\n[!] Error general capturado: {e}")
        # Impresión completa del stack de errores para debugging
        print(traceback.format_exc())

    print("\n[*] Ciclo de prueba finalizado. Pausando contenedor...")
    while True:
        time.sleep(3600)

if __name__ == "__main__":
    main()