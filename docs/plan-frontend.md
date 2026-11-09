# Arquitectura y alcance del frontend

## Estado y autorización

Página implementada y comprobada con API local: Tendidos/Capacidad, casos y crecimiento, detalle/tabla de barrios y comparación. Efectos elegidos por Ciro integrados. 43 pruebas, lint, TypeScript y build aprobados. La publicación actual en Vercel/Render no se verificó.

El usuario autorizó React + TypeScript estricto + Vite, CSS propio y SVG; asumió completar casos y abastecimiento por barrio. No se agregan autenticación, base de datos, uploads ni nuevos servicios. Otras mejoras visuales requieren consulta. Backend concentra ML, MST y flujo.

## Arquitectura

`App` coordina navegación, selección y parámetros. `useSimulacion` solicita el resultado principal e identifica caso/escenario mostrados. `api/cliente` controla HTTP, espera y cancelación; `api/validar` verifica el contrato. `lib/red` adapta datos para componentes y vistas.

Las vistas comparten la misma respuesta. Elegir Efectos no solicita otra simulación; HoloCard se carga de forma diferida. La comparación es una acción aparte: tres peticiones al mismo caso, sin modificar el resultado principal.

## Flujos de uso

1. Elegir Original o Progresivo y una tasa Base/+10 %/+30 %.
2. Explorar candidatos y MST, seleccionar barrios/tendidos y buscar en tabla.
3. Consultar caudales, cercanía/saturación, cobertura y suministro/déficit por barrio.
4. Comparar tres escenarios completos del caso seleccionado.
5. Reintentar errores conservando el resultado anterior identificado.

Las respuestas tardías no reemplazan al último caso/escenario. Cambiar de caso cancela la comparación anterior; si falla una respuesta, no hay tabla parcial. La API antigua solo se admite para Original y los datos ausentes quedan explícitos.

## Diseño y accesibilidad

Paleta de Ciro: #44749d, #c6d4e1, #ffffff, #ebe7e0, #bdb8ad. Texto oscuro y estados también expresados con palabras. Selección por teclado, foco visible y enlace para saltar al contenido. SVG y tablas desplazan internamente en móvil.

Sin distintivo live ni reloj de última respuesta. LatticeLoader acompaña solicitudes; su tiempo incluye red y servidor, no porcentaje de progreso. HoloCard queda en una pestaña separada con pausa y alternativa sin WebGL. Se respeta movimiento reducido. TechText no se aplica al grafo.

## Contrato y fuentes

API con PLANTA, barrios, MST, candidatos y todos los caudales. Resumen y abastecimiento por barrio se calculan en Python. El navegador no deduce suministro sumando cañerías. Usa geometría API; el CSV local solo completa respuestas anteriores coincidentes y no contiene predicciones.

Campos, tolerancias, casos conocidos y compatibilidad en [contrato-api.md](contrato-api.md). Regla progresiva y resultados en [casos-capacidad.md](casos-capacidad.md). Los fixtures están solo en tests.

## Verificación y pendientes de entrega

Pruebas de contrato, cliente, interacción, concurrencia, errores, balance y efectos aprobadas; recorrido Edge local en escritorio/móvil, incluida desconexión/reintento. Estado canónico en [verificacion-proyecto.md](verificacion-proyecto.md).

Actualizar/verificar API pública y frontend si se entrega URL; publicar en Vercel no es requisito del PDF. El README permite una demo local. No quedan páginas ni funciones obligatorias identificadas como faltantes.
