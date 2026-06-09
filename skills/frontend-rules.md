# Reglas de Arquitectura Frontend (DataHub - Módulo KyC)
- **Framework Principal:** SvelteKit estructurado con Svelte 5.
- **Estilos:** TailwindCSS.
- **Adaptador de Producción:** @sveltejs/adapter-node.
- **Renderizado (Obligatorio):** Configurar `ssr = false` y `prerender = false` en el archivo `+layout.ts` raíz para prevenir colisiones de estado en el entorno de producción.
- **Estado Reactivo:** Utilizar exclusivamente los nuevos Runes de Svelte 5 (`$state`, `$derived`, `$props`).
- **Directriz de Código:** Los componentes de interfaz web deben entregarse completos sin resúmenes.