const http = require('http');

const PORT = 3003;

const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/v1/chat/completions') {
    let body = '';
    
    req.on('data', chunk => { 
        body += chunk.toString(); 
    });
    
    req.on('end', () => {
      let responseContent = "Respuesta genérica del proxy.";
      
      // Analizar el prompt entrante para devolver una respuesta contextual según el rol del Agente
      if (body.includes("Desarrollador Full-Stack")) {
        console.log('[Windsurf Proxy] Petición interceptada: Agente Desarrollador');
        responseContent = "He revisado el plan del Arquitecto. He implementado el endpoint en FastAPI y su correspondiente componente en SvelteKit. El código ha sido optimizado y refactorizado en el entorno seguro.";
      } else if (body.includes("Ingeniero de QA")) {
        console.log('[Windsurf Proxy] Petición interceptada: Agente QA');
        responseContent = "He ejecutado las pruebas estáticas y revisado la lógica del Desarrollador. No se encontraron vulnerabilidades ni errores de sintaxis en el tipado de TypeScript ni en Pydantic. El código está listo para producción.";
      } else {
        console.log('[Windsurf Proxy] Petición interceptada: Agente Arquitecto');
        responseContent = "¡Hola, equipo! Soy el Arquitecto de Software AI.\n\nPropongo estos pasos:\n1. Analizar `/workspace/datahub`.\n2. Auditar la base de datos MongoDB.\n3. Identificar componentes UI.";
      }

      const response = {
        id: "chatcmpl-windsurf-mock",
        object: "chat.completion",
        created: Math.floor(Date.now() / 1000),
        model: "gpt-4-turbo",
        choices: [{
          index: 0,
          message: { role: "assistant", content: responseContent },
          finish_reason: "stop"
        }],
        usage: { prompt_tokens: 50, completion_tokens: 100, total_tokens: 150 }
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