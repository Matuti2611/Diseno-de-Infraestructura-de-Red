# Efectos visuales elegidos por Ciro

## Alcance implementado

Ciro aportó ejemplos de React Bits y el código de HoloCard. Se incorporaron HoloCard y LatticeLoader con sus variantes oficiales TypeScript/CSS, compatibles con React/Vite y el CSS existente. No se ejecutó el instalador de shadcn ni se añadieron paquetes, Tailwind o un framework nuevo.

- **HoloCard:** pestaña «Efectos» accesible también desde el menú lateral. Muestra la imagen Pikachu de la demostración oficial, guardada localmente; reflejos `bursts`, inclinación, sombra y parámetros visuales indicados por el usuario. La prop `preset` se declara una sola vez; `card="pikachu"` no forma parte de las props del componente: la imagen se entrega mediante `image`.
- **LatticeLoader:** reemplaza el texto de espera mientras existe una solicitud de simulación. Patrón orbit de 3×3, azul de la paleta, sin glow y contador de tiempo real de espera. Se reinicia al cambiar de escenario o reintentar, y desaparece ante éxito o error. No estima porcentaje de avance ni representa el tiempo exclusivo del algoritmo: incluye red, espera de Render y procesamiento.
- **TechText:** evaluado y sin aplicar, según la condición indicada por el usuario. Convierte letras en trazos vectoriales; no es un renderizador de grafos. Reemplazar el SVG de la red no aportaba a nodos, conexiones, etiquetas y selección existentes.

La tarjeta es una exploración visual independiente: no representa predicciones ni participa en el diagnóstico. Otras propuestas visuales se consultan con el usuario antes de implementarlas.

## Organización y adaptaciones

- `frontend/src/components/effects/`: código local de HoloCard/LatticeLoader y sus CSS. No se descarga código al abrir la página.
- `frontend/src/assets/pikachu.webp`: imagen local de la demostración, empaquetada por Vite.
- `frontend/src/views/VistaEfectos.tsx` y su CSS: presentación de la tarjeta y control para pausar la inclinación y el giro automático. La iluminación todavía responde al cursor.
- `App.tsx`: tercera sección y loader ligado al estado real. La vista de efectos se importa con `lazy`, para cargar el shader y la imagen al abrirla. La solicitud actual sigue su curso al cambiar de pestaña; volver a la red no solicita una simulación nueva.
- `useSimulacion.ts`: expone el número de intento para reiniciar el contador incluso cuando se reintenta el mismo escenario.

Se tradujeron etiquetas y anuncios del loader, se ocultó el reloj a lectores de pantalla para no anunciar cada décima, y se libera el intervalo al desmontar. Con movimiento reducido, la grilla queda estática. La tarjeta respeta cambios de esa preferencia, detiene su bucle al ocultarse y libera recursos al salir. Sin WebGL o al perderse su contexto, conserva la imagen HTML. Puede depender del rendimiento gráfico del dispositivo; la alternativa estática permite ver el contenido.

## Verificación

- **37 pruebas frontend aprobadas**, más lint, TypeScript y build. Cuatro pruebas nuevas comprueban reinicio del contador y retiro ante error/éxito, respuestas antiguas ignoradas durante la espera, limpieza del intervalo, alternativa sin WebGL y navegación de ida/vuelta sin nuevas solicitudes.
- Edge en escritorio: textura lista, imagen local cargada, inclinación/reflejos y pausa funcionando. En móvil de 390 px: tarjeta de 308 px y sin desbordamiento horizontal. La preferencia de movimiento reducido dejó de modificar su transformación.
- Al volver a Capacidad con Render real: 17 nodos, 16 caudales, tarjeta desmontada y loader retirado. Sin excepciones de JavaScript observadas.
- Build: bundle principal ~263 kB / 82 kB gzip; vista de efectos separada ~20 kB / 7 kB gzip; imagen ~49 kB. No cambió el lockfile por estos efectos.

No se modificaron el backend, los datos, los resultados de ML o los algoritmos como parte de esta incorporación. Sigue pendiente publicar el frontend en Vercel y repetir la instalación en otra computadora.

## Procedencia y licencia

React Bits es una fuente de código externo seleccionada por el usuario, no una herramienta de generación de IA. Codex integró y adaptó sus componentes. Se conserva el texto de licencia y la procedencia de la imagen en [THIRD_PARTY_NOTICES.md](../frontend/THIRD_PARTY_NOTICES.md). La carta y el personaje no se atribuyen al grupo ni a la IA.

- [Holo Card](https://reactbits.dev/components/holo-card)
- [LatticeLoader, código oficial](https://github.com/DavidHDev/react-bits/tree/main/src/ts-default/Micro/LatticeLoader)
- [Tech Text](https://reactbits.dev/text-animations/tech-text)
- [Registro HoloCard TypeScript/CSS](https://reactbits.dev/r/HoloCard-TS-CSS.json)
- [Registro LatticeLoader TypeScript/CSS](https://reactbits.dev/r/LatticeLoader-TS-CSS.json)
