const http = require('http');

const PORT = 3003;

const server = http.createServer((req, res) => {
  if (req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    
    req.on('end', () => {
      let responseContent = "¡Hola, equipo! Soy el Arquitecto de Software AI.\n\nPropongo estos pasos:\n1. Analizar `/workspace/datahub`.\n2. Auditar la base de datos MongoDB.\n3. Identificar componentes UI.";

      if (body.includes("Desarrollador Full-Stack")) {
        console.log('[Windsurf Proxy] Petición interceptada: Agente Desarrollador');
        responseContent = "He revisado el plan del Arquitecto. He implementado el endpoint en FastAPI y su correspondiente componente en SvelteKit. El código ha sido refactorizado en el entorno seguro.";
      } else if (body.includes("Ingeniero de QA")) {
        console.log('[Windsurf Proxy] Petición interceptada: Agente QA');
        responseContent = "He ejecutado las pruebas estáticas y revisado la lógica del Desarrollador. No se encontraron vulnerabilidades. El código está listo para producción.";
      } else {
        console.log('[Windsurf Proxy] Petición interceptada: Agente Arquitecto');
      }

      // El formato ReAct es obligatorio para que el parser de CrewAI no se rompa
      const reactFormatResponse = `Thought: I now can give a great answer\nFinal Answer: ${responseContent}`;

      // Forzamos cabeceras Server-Sent Events (SSE)
      res.writeHead(200, {
        'Content-Type': 'text/event-stream; charset=utf-8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
      });

      const id = "chatcmpl-mock-123";
      const created = Math.floor(Date.now() / 1000);

      // Bloque 1: Inicialización del rol
      res.write(`data: ${JSON.stringify({id, object: "chat.completion.chunk", created, model: "gpt-4-turbo", choices: [{ index: 0, delta: { role: "assistant", content: "" }, finish_reason: null }]})}\n\n`);
      
      // Bloque 2: Carga útil completa (sin usar delays que rompan la conexión)
      res.write(`data: ${JSON.stringify({id, object: "chat.completion.chunk", created, model: "gpt-4-turbo", choices: [{ index: 0, delta: { content: reactFormatResponse }, finish_reason: null }]})}\n\n`);
      
      // Bloque 3: Señal de parada estricta de OpenAI
      res.write(`data: ${JSON.stringify({id, object: "chat.completion.chunk", created, model: "gpt-4-turbo", choices: [{ index: 0, delta: {}, finish_reason: "stop" }]})}\n\n`);
      
      // Cierre del stream
      res.write('data: [DONE]\n\n');
      res.end();
    });
  } else {
    res.writeHead(404);
    res.end();
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[Windsurf Proxy] Servicio inicializado en el puerto ${PORT}`);
});