const http = require('http');

const PORT = 3003;

const server = http.createServer((req, res) => {
  // Atrapamos cualquier POST hacia el proxy (LangChain añade automáticamente /chat/completions)
  if (req.method === 'POST') {
    let body = '';
    
    req.on('data', chunk => { 
        body += chunk.toString(); 
    });
    
    req.on('end', () => {
      let responseContent = "¡Hola, equipo! Soy el Arquitecto de Software AI.\n\nPropongo estos pasos:\n1. Analizar `/workspace/datahub`.\n2. Auditar la base de datos MongoDB.\n3. Identificar componentes UI.";

      // Analizamos el cuerpo de la petición para definir el contexto
      if (body.includes("Desarrollador Full-Stack")) {
        console.log('[Windsurf Proxy] Petición interceptada: Agente Desarrollador');
        responseContent = "He revisado el plan del Arquitecto. He implementado el endpoint en FastAPI y su correspondiente componente en SvelteKit. El código ha sido refactorizado en el entorno seguro.";
      } else if (body.includes("Ingeniero de QA")) {
        console.log('[Windsurf Proxy] Petición interceptada: Agente QA');
        responseContent = "He ejecutado las pruebas estáticas y revisado la lógica del Desarrollador. No se encontraron vulnerabilidades. El código está listo para producción.";
      } else {
        console.log('[Windsurf Proxy] Petición interceptada: Agente Arquitecto');
      }

      const reactFormatResponse = `Thought: Comprendo la tarea asignada y puedo entregar el resultado.\nFinal Answer: ${responseContent}`;

      // FORZAMOS cabeceras de Server-Sent Events (SSE) sin condicionales
      res.writeHead(200, {
        'Content-Type': 'text/event-stream; charset=utf-8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
      });

      const id = "chatcmpl-mock-" + Date.now();
      const created = Math.floor(Date.now() / 1000);

      const sendChunk = (delta, finish_reason) => {
        const chunk = {
          id: id,
          object: "chat.completion.chunk",
          created: created,
          model: "gpt-4-turbo",
          choices: [{ index: 0, delta: delta, finish_reason: finish_reason }]
        };
        res.write(`data: ${JSON.stringify(chunk)}\n\n`);
      };

      // Fragmento 1: Declaración del rol
      sendChunk({ role: "assistant", content: "" }, null);

      // Fragmento 2...N: Transmisión palabra por palabra (emulación de LLM real)
      const words = reactFormatResponse.split(" ");
      let i = 0;

      const interval = setInterval(() => {
        if (i < words.length) {
          // Reconstruimos los espacios entre palabras
          sendChunk({ content: words[i] + (i < words.length - 1 ? " " : "") }, null);
          i++;
        } else {
          clearInterval(interval);
          
          // Fragmento Final: Señal de parada estricta requerida por OpenAI-Python
          sendChunk({}, "stop");
          res.write('data: [DONE]\n\n');
          res.end();
        }
      }, 20); // 20 milisegundos de retraso entre cada token
    });
  } else {
    res.writeHead(404);
    res.end();
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[Windsurf Proxy] Servicio inicializado en el puerto ${PORT}`);
});
