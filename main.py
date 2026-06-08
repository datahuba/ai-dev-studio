import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    api_url = os.getenv("WINDSURF_API_BASE", "Not set")
    print("Iniciando equipo de agentes AI Dev Studio...")
    print(f"Conectado al proxy Windsurf en: {api_url}")
    # Aquí se implementará la lógica de CrewAI / LangChain

if __name__ == "__main__":
    main()
