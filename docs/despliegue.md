# Opciones de despliegue

Evaluación iniciada el 2026-11-07. **Arquitectura elegida por el usuario: frontend en Vercel y backend en Render.** El 2026-11-08 el usuario completó el despliegue en `https://infraestructura-red-api.onrender.com`. Se verificaron `/docs`, `/openapi.json` y una petición de simulación base, todos con HTTP 200. La prueba confirma arranque y comunicación, no la corrección matemática de los cálculos. Se desconoce el plan elegido. El frontend sigue pendiente de implementación y publicación.

## Qué necesita alojarse

- Frontend: archivos de React/Vite compilados; el navegador ejecuta la interfaz.
- Backend: API FastAPI con Pandas, scikit-learn, NetworkX, Joblib, CSV y modelo exportado. La simulación se solicita por HTTP.
- El modelo se entrena antes del despliegue; la API carga el artefacto y realiza inferencia y cálculos de grafos.
- El MVP no necesita GPU, una base de datos ni almacenamiento de resultados persistente. Memoria y tiempos se deben medir con las dependencias reales antes de elegir recursos.

## Comparación

| Opción | Encaje y ventajas | Costos de implementación y riesgos |
| --- | --- | --- |
| Vercel para React + Render para FastAPI | Conserva la separación del repositorio. Render ejecuta FastAPI como servicio web; frontend y API pueden desplegarse por separado. | Dos configuraciones, dirección de API y CORS. Render gratuito se suspende tras 15 minutos sin tráfico y el reinicio puede tardar alrededor de un minuto; contemplar carga y tiempo de espera. |
| Todo en Vercel | Vercel soporta Vite y FastAPI/Python; permite mantener un proveedor. | Probar empaquetado de dependencias científicas, CSV, modelo y rutas del monorepo; verificar arranque y tiempos de funciones. El límite estándar documentado de Python es 500 MB sin comprimir. No se midió el paquete de este proyecto. |
| VPS para todo, o Vercel + VPS para API | Máquina virtual alquilada, con control del entorno y posibilidad de servir frontend y API juntos. | En un VPS autoadministrado el grupo configura procesos, HTTPS, actualizaciones y reinicios. La recomendación cambia si ya hay un VPS gestionado y disponible. |
| Vercel + AWS Lambda para API | AWS ejecuta código a demanda; permite alojar el cálculo sin administrar un servidor convencional. | Empaquetar dependencias/modelo para Lambda, elegir exposición HTTP y configurar permisos y entorno. Agrega trabajo sin una necesidad específica de AWS en la consigna. |

**Elección para el alcance actual:** Vercel para el frontend y Render para FastAPI. Se eligió por la estructura actual y el tiempo de entrega; requiere comprobar el backend real y elegir el plan antes de publicar. Las otras opciones quedan documentadas como alternativas evaluadas.

Lambda es una opción para alojar el backend, no un componente obligatorio por usar Vercel. Un VPS es otra forma de alojarlo y puede incluir ambos componentes.

No se fijan precios en este documento: antes de contratar se deben confirmar plan, región, límites vigentes, recursos necesarios y presupuesto. La oferta gratuita de un proveedor no garantiza que alcance para el modelo y las dependencias del proyecto.

## Preparación común pendiente

1. Ejecutar el backend con sus dependencias y reproducir las predicciones; fijar versiones compatibles con el modelo exportado.
2. Resolver los campos de API faltantes y verificar casos conocidos de MST, flujo y escenarios.
3. Página construida localmente: 22 tests, lint, TypeScript y build aprobados el 08/11/2026. Revisarla antes de publicar.
4. Revisar los imports y rutas de CSV/modelo para el directorio de ejecución elegido; incluir esos archivos en el paquete publicado.
5. Configurar dirección de API pública en el frontend y restringir CORS al origen esperado. No incorporar secretos al bundle del navegador.
6. Probar HTTPS, carga inicial de modelo, respuesta después de inactividad, errores, límites de memoria y una simulación completa desde otra máquina.

Los CSV y el modelo versionados pueden formar parte del despliegue como archivos de lectura. No depender de escribirlos o reentrenarlos en cada petición. En servicios con disco efímero, los cambios hechos durante la ejecución no persisten necesariamente tras reinicios o despliegues.

## Esbozo para Vercel + Render

- Vercel: seleccionar `frontend/` como raíz, compilar con `npm run build` y servir `dist/`. El build local ya funciona; se probó Node 24.20.0.
- Render: conservar la raíz del repositorio para que coincida con los imports y rutas actuales; instalación prevista `pip install -r backend/requirements.txt` y arranque previsto `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`.
- El navegador obtiene la página de Vercel y solicita las simulaciones a la API de Render. Los cálculos permanecen en Python.

El backend ya respondió desde la página local a los escenarios base y +30 %. La configuración/publicación del frontend en Vercel sigue pendiente. La dirección de API es configurable con `VITE_API_URL` y requiere recompilar al cambiarla.

## Pasos para arrancar

1. Crear cuenta en Render y Vercel con GitHub y autorizar acceso al repositorio. Si no aparece, coordinar el acceso con Matías, propietario del repositorio.
2. Antes de publicar la API, instalar y comprobar el backend desde la raíz del repo. Registrar versiones compatibles con el modelo exportado; `requirements.txt` todavía no fija versiones.
3. En Render elegir **New → Web Service**, conectar el repositorio y configurar:

| Ajuste | Valor para este repositorio |
| --- | --- |
| Branch | `main` |
| Root Directory | Vacío: raíz del repositorio |
| Runtime / Language | Python 3 |
| Build Command | `pip install -r backend/requirements.txt` |
| Start Command | `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` |
| Variable de entorno | `PYTHON_VERSION=3.12.10`, base local conocida; verificar también las versiones de scikit-learn/Joblib del modelo |

La raíz debe quedar en el repositorio completo por los imports `backend.app` y las rutas `backend/data/...`. Un directorio raíz `backend/` exigiría adaptar esos imports y rutas. El plan gratuito puede servir para una demo si alcanza la memoria; confirmar las limitaciones antes de elegirlo. No se autorizó contratar un plan pago.

4. Cuando el backend se haya publicado, abrir `https://<servicio>.onrender.com/docs` y ejecutar `POST /api/simular-red` con `{"escenario_crecimiento": 1.0}`. Revisar logs si falla la instalación, el arranque o la carga del modelo. Una respuesta correcta comprueba el recorrido HTTP, pero no reemplaza los tests matemáticos.
5. Revisar el frontend local siguiendo `frontend/README.md`. **Ya está implementado y su build funciona; todavía no se publicó.** El contrato parcial se identifica en pantalla y no impide revisar la interfaz.
6. Importar el mismo repositorio en Vercel con raíz `frontend`, preset Vite, Node 24.x, comando `npm run build` y salida `dist`. Usar `VITE_API_URL=https://infraestructura-red-api.onrender.com`, sin `/api` al final. El cliente ya consume esta variable. Configurar CORS en FastAPI con el origen real de Vercel. Vercel usa el JSON geométrico versionado y no necesita ejecutar Python.
7. Probar una simulación desde la página publicada, incluida la primera solicitud después de un periodo de inactividad. Guardar URLs reales y resultados verificados en el contexto; no dar por publicado un servicio solo por haberlo configurado.

## Referencias oficiales consultadas

- Vite en Vercel: https://vercel.com/docs/frameworks/frontend/vite
- FastAPI en Vercel: https://vercel.com/docs/frameworks/backend/fastapi
- Runtime Python y empaquetado: https://vercel.com/docs/functions/runtimes/python
- FastAPI en Render: https://render.com/docs/deploy-fastapi
- Versión de Python en Render: https://render.com/docs/python-version
- Directorio raíz y monorepos en Render: https://render.com/docs/monorepo-support
- Limitaciones del plan gratuito de Render: https://render.com/docs/free
- Definición de VPS y responsabilidades: https://aws.amazon.com/what-is/vps/
- AWS Lambda: https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
