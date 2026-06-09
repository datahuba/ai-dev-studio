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
        // Ignorar si el cuerpo no es JSON válido
      }

      let responseContent = "Respuesta genérica del proxy.";
      
      // Analizar el prompt entrante para devolver una respuesta contextual
      if (body.includes("Desarrollador Full-Stack")) {
        console.log('[Windsurf Proxy] Petición interceptada: Agente Desarrollador');
        responseContent = "He revisado el plan del Arquitecto. He implementado el endpoint en FastAPI y su correspondiente componente en SvelteKit. El código ha sido refactorizado en el entorno seguro.";
      } else if (body.includes("Ingeniero de QA")) {
        console.log('[Windsurf Proxy] Petición interceptada: Agente QA');
        responseContent = "He ejecutado las pruebas estáticas y revisado la lógica del Desarrollador. No se encontraron vulnerabilidades. El código está listo para producción.";
      } else {
        console.log('[Windsurf Proxy] Petición interceptada: Agente Arquitecto');
        responseContent = "¡Hola, equipo! Soy el Arquitecto de Software AI.\n\nPropongo estos pasos:\n1. Analizar `/workspace/datahub`.\n2. Auditar la base de datos MongoDB.\n3. Identificar componentes UI.";
      }

      // Estructura ReAct requerida por CrewAI
      const reactFormatResponse = `Thought: Comprendo la tarea asignada y puedo entregar el resultado.\nFinal Answer: ${responseContent}`;

      if (reqObj.stream) {
        // Cabeceras estrictas para streaming de eventos (SSE)
        res.writeHead(200, {
          'Content-Type': 'text/event-stream; charset=utf-8',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
          'Transfer-Encoding': 'chunked'
        });

        const id = "chatcmpl-mock-" + Date.now();
        const created = Math.floor(Date.now() / 1000);
        const model = reqObj.model || "gpt-4-turbo";

        const sendChunk = (delta, finish_reason) => {
          const chunk = {
            id: id,
            object: "chat.completion.chunk",
            created: created,
            model: model,
            choices: [{ index: 0, delta: delta, finish_reason: finish_reason }]
          };
          res.write(`data: ${JSON.stringify(chunk)}\n\n`);
        };

        // Despacho asíncrono para garantizar que los paquetes se transmitan por separado
        setTimeout(() => {
          sendChunk({ role: "assistant", content: "" }, null);
        }, 100);

        setTimeout(() => {
          sendChunk({ content: reactFormatResponse }, null);
        }, 300);

        setTimeout(() => {
          sendChunk({}, "stop");
        }, 500);

        setTimeout(() => {
          res.write('data: [DONE]\n\n');
          res.end();
        }, 700);

      } else {
        // Respuesta JSON estándar
        const response = {
          id: "chatcmpl-mock",
          object: "chat.completion",
          created: Math.floor(Date.now() / 1000),
          model: reqObj.model || "gpt-4-turbo",
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
