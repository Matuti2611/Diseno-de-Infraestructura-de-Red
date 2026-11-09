# Despliegue: Vercel + Render

Arquitectura elegida: frontend estático React/Vite en Vercel y FastAPI en Render. La consigna exige demo end-to-end y README reproducible, no hosting público. La demo local y las pruebas están comprobadas; la publicación actual del último código no se confirmó.

No hacen falta Lambda, VPS, autenticación ni base de datos para el alcance entregado. No se contrataron servicios desde estas revisiones.

## Orden de publicación

1. Registrar y subir los cambios finales cuando el usuario lo autorice.
2. Actualizar/verificar primero la API de Render.
3. Probar la página con esa API y compilar/publicar frontend en Vercel.
4. Comprobar desde la URL final los dos casos, comparación, barrios, errores/reintento y móvil.

## Render: API

Conservar raíz del repositorio completa: las rutas/imports usan backend/... .

| Ajuste | Valor |
| --- | --- |
| Rama | main |
| Root Directory | Vacío |
| Runtime | Python |
| Build Command | pip install -r backend/requirements.txt |
| Start Command | uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT |
| Python | 3.12.10 en .python-version; si existe PYTHON_VERSION, debe coincidir |

API conocida: `https://infraestructura-red-api.onrender.com`. No confundir su existencia con tener el código final. Modelo y CSV van versionados como archivos de lectura, sin entrenar ni generarlos por petición.

En /docs probar POST /api/simular-red con `{"caso_red":"progresivo","escenario_crecimiento":1.3}`. Debe confirmar caso/crecimiento y entregar suministro/déficit por barrio. Los resultados esperados locales están en [casos-capacidad.md](casos-capacidad.md). Una API anterior puede ignorar el campo: el cliente lo detecta.

## Vercel: permisos e importación

Si el repositorio pertenece a una cuenta personal de GitHub, debe importarlo su propietario; un colaborador no puede hacerlo solo por habilitar la app. En una organización se requiere ser miembro con permisos adecuados. Un fork propio requiere sincronización.

En la cuenta que tenga el acceso necesario:

1. Add New → Project → buscar repositorio → Import.
2. Si falta, Configure GitHub App → autorizar ese repositorio desde su cuenta propietaria.
3. Root Directory: frontend; Framework Preset: Vite.
4. Confirmar vercel.json: npm ci, npm run build, salida dist.
5. Node 24.x, fijado por engines del package.json.
6. Agregar VITE_API_URL=`https://infraestructura-red-api.onrender.com`, sin /api al final.
7. Deploy y comprobar la versión construida y la URL HTTPS.

La variable es pública y se incorpora al bundle; cambiarla requiere reconstruir. La aplicación no tiene rutas de React Router que necesiten reglas de reescritura. No ejecutar Python en el build frontend.

## Comprobación final

Probar dos casos, tres crecimientos, tabla/detalle de barrios, comparación y acceso móvil. El primer inicio del servicio puede demorar: el cliente espera hasta 90 s y permite reintentar. Comprobar también respuesta tras inactividad.

CORS actual permite cualquier origen sin credenciales. Revisar con el origen Vercel definitivo y los entornos que se usen antes de restringirlo. Guardar URL y resultados solo cuando se comprueben; no se publicaron servicios automáticamente desde la revisión de cierre.

## Referencias

- [Vite en Vercel](https://vercel.com/docs/frameworks/frontend/vite)
- [Permisos GitHub en Vercel](https://vercel.com/docs/git/vercel-for-github)
- [Node en Vercel](https://vercel.com/docs/functions/runtimes/node-js/node-js-versions)
- [FastAPI en Render](https://render.com/docs/deploy-fastapi)
- [Python en Render](https://render.com/docs/python-version)
