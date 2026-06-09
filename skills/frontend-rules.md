# Reglas de Arquitectura Frontend (DataHub - Módulo KyC)
- **Framework Principal:** SvelteKit estructurado con Svelte 5.
- **Estilos:** TailwindCSS.
- **Adaptador de Producción:** @sveltejs/adapter-node.
- **Renderizado (Obligatorio):** Configurar `ssr = false` y `prerender = false` en el archivo `+layout.ts` raíz para prevenir colisiones de estado en el entorno de producción.
- **Estado Reactivo:** Utilizar exclusivamente los nuevos Runes de Svelte 5 (`$state`, `$derived`, `$props`).
- **Manejadores de Eventos:** En Svelte 5 los eventos ya no usan el prefijo `on:`. Debes usar atributos nativos en minúsculas (ejemplo: usa `onclick={mifuncion}` en lugar de `on:click={mifuncion}`).
- **Directriz de Código:** Los componentes de interfaz web deben entregarse completos sin resúmenes ni comentarios de relleno.
