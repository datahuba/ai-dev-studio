import os
def verify_workspace_environment():
    print("--- INICIANDO VERIFICACIÓN DE ENTORNO DE AGENTES ---")
    api_base = os.getenv("OPENAI_API_BASE", "http://windsurf-api:3003/v1")
    workspace_dir = os.getenv("WORKSPACE_DIR", "/workspace/datahub")
    print(f"Base de la API de IA: {api_base}")
    print(f"Directorio de Trabajo Configurado: {workspace_dir}")
    if os.path.exists(workspace_dir):
        print(f"? El directorio de trabajo {workspace_dir} existe y es accesible.")
        try:
            files = os.listdir(workspace_dir)
            print(f"Archivos encontrados en la raíz del proyecto: {files}")
        except Exception as e:
            print(f"? Error al intentar listar el directorio: {str(e)}")
    else:
        print(f"? Error: El directorio {workspace_dir} no se encuentra o el volumen no está montado.")
    skills_dir = "/workspace/skills"
    if os.path.exists(skills_dir):
        print(f"? El directorio de habilidades {skills_dir} existe de forma correcta.")
    else:
        print(f"?? Advertencia: El directorio {skills_dir} no está disponible localmente.")
if __name__ == "__main__":
    verify_workspace_environment()
