const http = require('http');

const PORT = 3003;

const server = http.createServer((req, res) => {
  // LangChain envía las peticiones a la ruta estándar de OpenAI
  if (req.method === 'POST' && req.url === '/v1/chat/completions') {
    let body = '';
    
    req.on('data', chunk => { 
        body += chunk.toString(); 
    });
    
    req.on('end', () => {
      console.log('[Windsurf Proxy] Petición interceptada de la red AI.');
      
      // Estructura de respuesta (Mock) compatible con el parser de LangChain/CrewAI
      const response = {
        id: "chatcmpl-windsurf-mock",
        object: "chat.completion",
        created: Math.floor(Date.now() / 1000),
        model: "gpt-4-turbo",
        choices: [{
          index: 0,
          message: {
            role: "assistant",
            content: "¡Hola, equipo! Soy el Arquitecto de Software AI.\n\nPara iniciar el desarrollo, propongo estos 3 pasos:\n\n1. **Lectura de Sandbox:** Analizar la estructura del código montado en `/workspace/datahub`.\n2. **Revisión de Modelos:** Auditar los esquemas Pydantic y Beanie ODM (MongoDB) del backend FastAPI.\n3. **Mapeo de UI:** Identificar el árbol de componentes de SvelteKit en el frontend."
          },
          finish_reason: "stop"
        }],
        usage: { prompt_tokens: 15, completion_tokens: 85, total_tokens: 100 }
      };

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(response));
    });
  } else {
    res.writeHead(404);
    res.end(JSON.stringify({ error: "Endpoint no encontrado" }));
  }
});

server.listen(PORT, () => {
  console.log(`[Windsurf Proxy] Servicio inicializado en el puerto ${PORT}`);
});