# Reglas de Arquitectura Backend (DataHub - Módulo KyC)
- **Framework Principal:** FastAPI (Python) ejecutado sobre un servidor asíncrono Uvicorn.
- **Base de Datos:** MongoDB Atlas (Cloud).
- **Object Document Mapper (ODM):** Beanie.
- **Validación de Datos:** Esquemas Pydantic v2 obligatorios.
- **Middlewares:** Implementar GZipMiddleware para comprimir respuestas JSON mayores a 1KB.
- **Directriz de Código:** Todo controlador, ruta (router) o modelo generado debe entregarse completo. Queda estrictamente prohibido omitir secciones o usar comentarios como "// resto del código".