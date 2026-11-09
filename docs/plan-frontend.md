# Propuesta de página y arquitectura inicial

## Ampliación aprobada e implementada

Ciro asumió completar las mejoras de capacidad: selector de casos original/progresivo, suministro/déficit por barrio y comparación Base/+10 %/+30 %. Implementadas con React/CSS existentes y cálculos en backend, sin dependencias nuevas. El original se conserva; las peticiones identifican el caso y se descartan respuestas desactualizadas. Las comparaciones requieren tres balances completos y se cancelan al cambiar de caso. Ver `casos-capacidad.md`.

Verificación actual: 43 pruebas frontend, lint, TypeScript y build aprobados; integración de navegador con API local y móvil sin desbordamiento. Falta publicar/verificar API nueva en Render y frontend en Vercel. Las comprobaciones previas de Render que siguen describen el contrato anterior.

Estado: **página integrada con el contrato completo real de Render**, 16 caudales y balance visibles. Pasaron 43 pruebas, lint, TypeScript y build. El cliente admite `metricas_ml: null`, como la corrección local del backend. Faltan publicación de correcciones, Vercel y prueba en otra máquina; ver `verificacion-proyecto.md`. El registro de errores/resoluciones está en la sección de IA del informe.

Ciro aportó referencias de React Bits: se implementó HoloCard con Pikachu en una pestaña especial y LatticeLoader durante la carga real. TechText no se aplicó porque anima letras y no sustituye el SVG interactivo de la red. Sin dependencias adicionales ni Tailwind; detalle en `efectos-visuales.md`. Otras mejoras visuales requieren consulta al usuario. Node 24.x, `.nvmrc` y `vercel.json` ya están preparados. Una instalación nueva anterior a estos efectos pasó las verificaciones; el ensayo en otra computadora sigue pendiente, con pasos en `instalacion-reproducible.md`.

### Implementación actual frente al plan

Se implementaron las dos vistas, selección SVG/tabla, escenarios, búsqueda, carga/error/reintento y paleta. Se usa API real; los fixtures están solo en tests. La API actual entrega todos los caudales y el balance; Sin dato/diagnóstico incompleto se conservan para respuestas parciales. Los escenarios multiplican la tasa de crecimiento poblacional, como el predictor.

Cada arista del MST muestra caudal/utilización o Sin dato. El panel usa el `resumen_capacidad` real, con los campos implementados por Matías. Se comprobaron tres escenarios por HTTP y el recorrido en Edge, sin modificar el frontend. Contrato en `contrato-api.md` y requisitos en `revision-consigna.md`. La sección de IA registra paleta, Figma y patrones previos de Ciro presentes en este alcance.

Se priorizan planta y candidatos de la API. La geometría/costos/capacidades CSV (`casoRed.json`) quedan como compatibilidad con respuestas antiguas, solo tras comprobar coincidencia del caso. No se generan predicciones ni algoritmos en navegador. Sincronización y ejecución: `../frontend/README.md`.

## 1. Objetivo y usuarios

La página permite inspeccionar el diseño de una red de agua y comprobar cómo cambia su capacidad de abastecimiento ante diferentes demandas. La acción principal es elegir un escenario y ver qué red se construye, cuánto cuesta y si abastece a todos los barrios.

Usuarios iniciales: integrantes del grupo, docentes y una persona que evalúe la planificación de la cooperativa. Comparten una vista de consulta y simulación. El MVP no requiere cuentas, permisos diferenciados ni administración de registros.

## 2. Alcance

| MVP | Posterior | Futuro |
| --- | --- | --- |
| Planta, barrios y conexiones candidatas | Comparación simultánea de escenarios | Edición de escenarios y redes |
| MST resaltado y costo total | Exportar resultados | Historial persistente y colaboración |
| Flujos, capacidades y déficit | Análisis de errores del modelo más detallado | Mapa geográfico con calles y servicios externos |
| Escenarios base, +10 % y +30 % | Más filtros y escenarios | Modelado hidráulico más detallado |
| Tabla, leyenda, carga, errores y reintento | Mejoras de presentación | Roles, solo si surge una necesidad real |
| Métricas reales cuando estén disponibles | | |

## 3. Páginas, navegación y presentación

Un único panel con dos vistas: **Tendidos** y **Capacidad**. El encabezado identifica el proyecto y el escenario activo; una navegación permite cambiar de vista. Un bloque compacto explica los datos sintéticos y el método. No se necesita una portada comercial ni rutas privadas.

- Tendidos: conexiones candidatas, MST resaltado, costo total y detalle de aristas.
- Capacidad: demanda y suministro en m³/día, déficit, flujos por arista, estados de utilización y tabla.
- Escritorio: grafo y resumen en columnas; tabla debajo. Móvil/tablet: bloques apilados, controles accesibles y tabla con desplazamiento horizontal si hace falta.
- El grafo tiene leyenda y selección de un nodo/arista con detalle. La tabla ofrece acceso equivalente a la información. Los estados usan texto además de color.

Dirección visual: panel técnico claro, con la paleta elegida por el usuario. La prioridad es la lectura del grafo, las cifras y el diagnóstico. Los efectos aprobados se limitan al loader y la tarjeta en una pestaña propia.

Revisión del usuario: evitar distintivos tipo «en vivo» y estados técnicos de API en la cabecera. Se quitaron ese indicador y la hora de respuesta; la carga se comunica con texto sencillo junto al escenario y los fallos con reintento.

| Color | Papel previsto |
| --- | --- |
| `#44749d` | Azul principal: botones, selección, foco y red elegida |
| `#c6d4e1` | Azul claro: superficies de apoyo y selección suave |
| `#ffffff` | Tarjetas, tablas y superficies de lectura |
| `#ebe7e0` | Fondo general cálido |
| `#bdb8ad` | Separadores y bordes decorativos |

Al implementar, expresar estos colores como variables CSS con nombres semánticos para mantener el estilo coherente. El contraste calculado entre blanco y azul principal es 4,96:1; entre azul principal y fondo cálido es 4,03:1. El gris y el azul claro tienen poco contraste sobre blanco: reservarlos para superficies o decoración. Usar un tono de texto oscuro derivado de la paleta para lectura sobre fondos claros y un foco bien visible; comprobar los estados concretos del diseño, no solo los colores aislados. Los diagnósticos de capacidad deberán identificarse también con texto y símbolos.

## 4. Flujos y estados

Abrir panel → cargar red y escenario base → inspeccionar tendidos → cambiar a capacidad → elegir crecimiento → solicitar simulación → mostrar resultados del escenario solicitado.

Estados necesarios: carga inicial, simulación en curso, éxito, error de conexión con reintento, respuesta inválida, red vacía y simulación con demanda insatisfecha. La insuficiencia de capacidad es un resultado válido del análisis.

Una respuesta vieja no debe sobrescribir un escenario más reciente. Deshabilitar solicitudes duplicadas o cancelar/ignorar la anterior; anunciar carga y error de forma accesible. Si se conserva un resultado previo durante una solicitud, identificar a qué escenario pertenece.

## 5. Entidades, contratos y fuente de verdad

El esquema actual de Matías es el punto de partida. Antes de implementar el intercambio, acordar:

| Entidad | Información necesaria |
| --- | --- |
| Escenario | Multiplicador numérico positivo y finito; presets 1.0, 1.1 y 1.3 |
| Nodo | ID único, coordenadas, tipo/rol y demanda diaria no negativa |
| Arista candidata | Extremos existentes, costo y capacidad; misma identidad en ambas vistas |
| MST | Subconjunto de conexiones candidatas y costo total |
| Estado de flujo | Extremos, flujo, capacidad y estado de utilización |
| Resumen | Demanda total, caudal suministrado, déficit y unidad m³/día |
| Métricas ML | MAE, RMSE, R² y unidad de los errores; solo resultados reales disponibles |

`POST /api/simular-red` ya entrega planta, candidatos, todos los flujos y resumen; se comprobó el contrato completo en Render. Hay consultas auxiliares de red, pero la página obtiene su resultado consistente mediante la simulación única.

También acordar la semántica del escenario: el esquema lo describe como multiplicador de demanda, mientras que el predictor actual multiplica la tasa de crecimiento poblacional. El texto del selector debe reflejar el cálculo efectivo del backend.

La API valida escenarios y es responsable de predicciones, selección del MST, flujos y totales. El frontend envía el escenario y presenta la respuesta. CSV, JSON y tipos TypeScript deben compartir un mapeo explícito de nombres y unidades; el consumo mensual se convierte a diario en backend.

El cliente comprueba la forma de la respuesta en el límite con el servidor: números finitos, colecciones y campos necesarios. Se propone una validación pequeña y específica sin agregar Zod de entrada. Un fallo de validación se presenta como error, no como una red de demanda cero.

Modo demostración: datos de ejemplo identificados como tales, con resultados conocidos para probar la interfaz. No afirmar que son predicciones obtenidas para los 16 barrios ni fabricar métricas. El cambio a API real es explícito; una caída del backend no activa una demostración silenciosa.

## 6. Alternativas de arquitectura

| Alternativa | Ventajas | Costos/riesgos | Dificultad e impacto |
| --- | --- | --- | --- |
| React + TypeScript + Vite | Encaja con el repositorio y consume directamente FastAPI; salida estática | Requiere cerrar contrato y configurar acceso al backend | Baja/media; permite ampliar el panel sin mover los cálculos |
| Next.js + React | Útil si luego se necesitan páginas con renderizado de servidor | Introduce responsabilidades de servidor adicionales y despliegue más complejo para esta división Python/React | Media/alta; migración del esqueleto actual |
| TypeScript y DOM sin React | Menor cantidad de herramientas de interfaz | Más coordinación manual entre grafo, tabla y escenarios | Media; menos alineado con la estructura acordada |

**Recomendación:** React + TypeScript estricto + Vite, conservando el backend Python. No se propone PostgreSQL ni Prisma: el MVP consulta datos sintéticos y ejecuta cálculos, sin registros editables ni historial persistente. No requiere migraciones ni cambios de base de datos.

Para estilos, CSS propio es suficiente para estas dos vistas y evita incorporar otra herramienta. Tailwind es una alternativa si el grupo prefiere sus utilidades; no es necesario para cumplir el alcance. SVG nativo alcanza para representar 17 nodos; una librería de mapas o grafos agregaría APIs y dependencias antes de necesitarlas.

## 7. Dependencias propuestas y verificación

| Herramienta | Para qué sirve | Alternativa/decisión |
| --- | --- | --- |
| React y React DOM | Interfaz con vistas y estado compartido | DOM manual; se recomienda React por la estructura existente |
| TypeScript | Contratos y detección de incompatibilidades | JavaScript; mantener tipado estricto |
| Vite y su integración React | Desarrollo y compilación del frontend | Next.js; se recomienda Vite por el alcance |
| Vitest + Testing Library + entorno DOM | Pruebas de escenarios, interacción y errores visibles | Pruebas solo de funciones con Node cubren menos interacción; se recomiendan herramientas de componentes |
| ESLint y configuración TypeScript/React mínima | Detectar problemas estáticos de código | Revisión manual; agregar configuración pequeña y útil |

Estas herramientas ya están instaladas y se guardó `package-lock.json`; se verificaron Node 24.20.0, React 19.3.1, Vite 7.3.7, TypeScript 5.9.3, Vitest 4.1.12 y ESLint 10.14.0. Se incluyeron tipos de React y DOM de pruebas, sin servicio externo de testing. Los overrides transitivos de minimatch para lint y su motivo se documentan en `../frontend/README.md`.

Comprobaciones para cerrar una etapa de frontend: tests relevantes, lint, TypeScript y build. Una prueba de navegador del recorrido principal se agrega cuando exista una integración comprobable y un entorno de navegador disponible.

## 8. Estado y persistencia

- Estado de React: vista activa, escenario seleccionado, selección del grafo y estado de solicitudes.
- Datos del servidor: respuesta de red/simulación y métricas disponibles, sin duplicar la lógica de cálculo.
- MVP sin persistencia propia: al refrescar se vuelve al escenario base y se vuelve a cargar; volver a abrir el navegador sigue el mismo comportamiento.
- URL con escenario/vista compartibles puede agregarse después. No se necesitan localStorage, cookies ni base de datos inicialmente.

## 9. Seguridad, accesibilidad y entornos

Validar el escenario en servidor; el navegador no determina totales ni capacidades. Mostrar textos como contenido, no interpretar HTML devuelto por la API. No exponer secretos en configuración del frontend. La dirección de la API es configuración pública; CORS se configura en FastAPI para el origen de la página.

Local: desarrollo con API real de Render o dirección local configurable. El usuario eligió Vercel para frontend y Render para FastAPI; ver [despliegue.md](despliegue.md). La página consulta `https://infraestructura-red-api.onrender.com` y usa `VITE_API_URL`; los escenarios reales se verificaron en navegador. Su publicación sigue pendiente. No se necesitan pagos, email, uploads ni autenticación para el MVP.

Usar HTML semántico, labels, controles por teclado, foco visible y contraste suficiente. Ofrecer tabla y leyenda como complemento del SVG y mensajes de carga/error comprensibles para tecnologías de asistencia.

## 10. Archivos que se tocarían al implementar

Conservar los archivos existentes y completar su responsabilidad:

```text
frontend/
  index.html                         # Nuevo: entrada HTML
  package.json                       # Scripts y dependencias aprobadas
  tsconfig.json, vite.config.ts       # Configuración
  src/
    main.tsx, App.tsx                 # Entrada y coordinación del panel
    types/red.ts                     # Contrato TypeScript acordado
    api/cliente.ts                   # Solicitudes y validación de respuesta
    api/validar.ts                   # Validación del contrato recibido
    data/casoRed.json                # Geometría de CSV, sin predicciones
    lib/red.ts                       # Adaptación y formatos para presentar
    hooks/useSimulacion.ts            # Nuevo: estado de carga y concurrencia
    components/                      # MapaRed, SelectorEscenario, PanelDiagnostico,
                                     # TablaAristas y Leyenda ya previstos
    views/                           # VistaTendidos y VistaFlujo ya previstas
    styles/global.css                # Nuevo: diseño y responsive
    tests/                           # Nuevas pruebas del comportamiento importante
```

Se agregaron configuración de pruebas/lint, lockfile y `.env.example`. Los fixtures están en `src/tests/fixtures/`; no hay proveedor demo de producción porque Render ya estaba disponible. Actualizar README, contexto e informe en cada etapa. Los cambios de `schemas.py` y routers deben coordinarse con Matías; esta implementación no los modifica.

## 11. Riesgos y pruebas con resultados comprobables

- Contrato incompleto: acordar conexiones candidatas, resumen, unidades y errores antes de integrar. Probar respuestas incompletas o incompatibles.
- Backend pendiente: usar fixture explícito para avanzar y pasar a API real antes de declarar completa la demo del proyecto.
- Escenarios distintos mezclados: probar respuestas fuera de orden y comprobar que se muestra el escenario seleccionado.
- Unidades o estados incorrectos: probar valores conocidos en tabla, grafo y resumen; acordar umbral cercano a saturación (propuesta: 90 %).
- Saturación y déficit: probar que se muestran como resultados válidos y no como fallas de conexión.
- Dependencias innecesarias: incorporar solo las justificadas y aprobadas. La página no reemplaza ML ni algoritmos de Matías.

Ejemplo de integración de referencia: capacidad PLANTA–A=70 y A–B=35 m³/día; demandas A=20 y B=30. Base: demanda/suministro 50/50 y déficit 0. +30 %: demanda 65, suministro 61 y déficit 4. El frontend debe presentar esos resultados provenientes de una fixture conocida o de la API, sin calcular el flujo máximo.

## 12. Etapas y aprobación

1. Guardar y compartir esta arquitectura; acordar los detalles del contrato de datos con Matías.
2. Configurar React/Vite/TypeScript y herramientas mínimas; primera vista de tendidos con datos de ejemplo identificados.
3. Agregar capacidad, escenarios, tabla, accesibilidad, responsive y pruebas de comportamiento.
4. Conectar FastAPI, probar errores y escenarios reales, verificar tests/lint/tipos/build.
5. Completar informe, capturas, instrucciones y decisión de despliegue.

La aprobación de este plan habilita su alcance inicial; las ampliaciones sustanciales o servicios nuevos se vuelven a plantear al usuario.

## Referencias técnicas

Documentación oficial consultada:

- Vite, opciones de inicio: https://vite.dev/guide/
- Vite, compilación para hosting estático: https://vite.dev/guide/build
- Vitest, escritura de pruebas: https://vitest.dev/guide/learn/writing-tests
- Testing Library, pruebas orientadas al uso: https://testing-library.com/docs/guiding-principles/
