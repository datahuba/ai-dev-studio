const http = require('http');

const PORT = 3003;

const server = http.createServer((req, res) => {
  if (req.method === 'POST' && req.url === '/v1/chat/completions') {
    let body = '';
    
    req.on('data', chunk => { 
        body += chunk.toString(); 
    });
    
    req.on('end', () => {
      let reqObj = {};
      try {
        reqObj = JSON.parse(body);
      } catch (e) {
        // Ignorar error de parseo si el cuerpo no es JSON
      }

      let responseContent = "Respuesta genérica del proxy.";
      
      // Analizar el prompt entrante para devolver una respuesta contextual
      if (body.includes("Desarrollador Full-Stack")) {
        console.log('[Windsurf Proxy] Petición interceptada: Agente Desarrollador');
        responseContent = "He revisado el plan del Arquitecto. He implementado el endpoint en FastAPI y su correspondiente componente en SvelteKit. El código ha sido optimizado en el entorno seguro.";
      } else if (body.includes("Ingeniero de QA")) {
        console.log('[Windsurf Proxy] Petición interceptada: Agente QA');
        responseContent = "He ejecutado las pruebas estáticas y revisado la lógica del Desarrollador. No se encontraron vulnerabilidades. El código está listo para producción.";
      } else {
        console.log('[Windsurf Proxy] Petición interceptada: Agente Arquitecto');
        responseContent = "¡Hola, equipo! Soy el Arquitecto de Software AI.\n\nPropongo estos pasos:\n1. Analizar `/workspace/datahub`.\n2. Auditar la base de datos MongoDB.\n3. Identificar componentes UI.";
      }

      const reactFormatResponse = `Thought: Comprendo la tarea asignada y puedo entregar el resultado.\nFinal Answer: ${responseContent}`;

      // LangChain Agent Executor utiliza internamente .stream(), lo que exige Server-Sent Events (SSE)
      if (reqObj.stream) {
        res.writeHead(200, {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive'
        });

        // Chunk 1: Envío del contenido
        const chunk1 = {
          id: "chatcmpl-windsurf-mock",
          object: "chat.completion.chunk",
          created: Math.floor(Date.now() / 1000),
          model: "gpt-4-turbo",
          choices: [{ index: 0, delta: { role: "assistant", content: reactFormatResponse }, finish_reason: null }]
        };
        res.write(`data: ${JSON.stringify(chunk1)}\n\n`);

        // Chunk 2: Señal de finalización
        const chunk2 = {
          id: "chatcmpl-windsurf-mock",
          object: "chat.completion.chunk",
          created: Math.floor(Date.now() / 1000),
          model: "gpt-4-turbo",
          choices: [{ index: 0, delta: {}, finish_reason: "stop" }]
        };
        res.write(`data: ${JSON.stringify(chunk2)}\n\n`);

        // Cierre de stream estándar de OpenAI
        res.write('data: [DONE]\n\n');
        res.end();
      } else {
        // Respuesta JSON estándar
        const response = {
          id: "chatcmpl-windsurf-mock",
          object: "chat.completion",
          created: Math.floor(Date.now() / 1000),
          model: "gpt-4-turbo",
          choices: [{
            index: 0,
            message: { role: "assistant", content: reactFormatResponse },
            finish_reason: "stop"
          }],
          usage: { prompt_tokens: 50, completion_tokens: 100, total_tokens: 150 }
        };

        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(response));
      }
    });
  } else {
    res.writeHead(404);
    res.end(JSON.stringify({ error: "Endpoint no encontrado" }));
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[Windsurf Proxy] Servicio inicializado en el puerto ${PORT}`);
});