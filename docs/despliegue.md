# Opciones de despliegue

**Arquitectura elegida: frontend en Vercel y backend en Render.** El backend está en `https://infraestructura-red-api.onrender.com`; se verificaron OpenAPI y tres simulaciones HTTP 200 con 17 nodos, 26 candidatos, 16 caudales y balance completo. La página local consume esa respuesta y ya está implementada; su publicación sigue pendiente. Se desconoce el plan elegido. El estado técnico está en `verificacion-proyecto.md`.

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

1. Dependencias compatibles fijadas (artefacto scikit-learn 1.9.1), Python 3.12.10 y Node 24.x registrados. Una copia separada con entornos nuevos pasó instalación, `pip check`, 22 tests backend, las 33 pruebas frontend anteriores a los efectos, lint y build con TypeScript. Los efectos no agregan paquetes. Falta repetir el recorrido en otra computadora; ver [instalación reproducible](instalacion-reproducible.md).
2. Contrato completo disponible en Render y recorrido verificado en la página. Las correcciones de inferencia, métricas y topología ya pasaron pruebas/HTTP local; falta publicarlas y verificarlas en Render. El registro de error/detección/solución está en la sección de IA del informe.
3. Página construida localmente, incluidos efectos: 37 tests, lint, TypeScript y build aprobados. Publicación pendiente.
4. Revisar los imports y rutas de CSV/modelo para el directorio de ejecución elegido; incluir esos archivos en el paquete publicado.
5. Configurar dirección de API pública en el frontend y restringir CORS al origen esperado. No incorporar secretos al bundle del navegador.
6. Probar HTTPS, carga inicial de modelo, respuesta después de inactividad, errores, límites de memoria y una simulación completa desde otra máquina.

Los CSV y el modelo versionados pueden formar parte del despliegue como archivos de lectura. No depender de escribirlos o reentrenarlos en cada petición. En servicios con disco efímero, los cambios hechos durante la ejecución no persisten necesariamente tras reinicios o despliegues.

## Esbozo para Vercel + Render

- Vercel: seleccionar `frontend/` como raíz. Su `vercel.json` indica preset Vite, instalación `npm ci`, build `npm run build` y salida `dist/`. `package.json` fija Node 24.x; se probó localmente 24.20.0. Vercel actualiza las versiones menores y parches de esa versión mayor.
- Render: conservar la raíz del repositorio para que coincida con los imports y rutas actuales; instalación prevista `pip install -r backend/requirements.txt` y arranque previsto `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`.
- El navegador obtiene la página de Vercel y solicita las simulaciones a la API de Render. Los cálculos permanecen en Python.

El backend ya respondió desde la página local a los escenarios base y +30 %. La configuración/publicación del frontend en Vercel sigue pendiente. La dirección de API es configurable con `VITE_API_URL` y requiere recompilar al cambiarla.

## Pasos para arrancar

1. Crear cuenta en Render y Vercel con GitHub y autorizar acceso al repositorio. Si no aparece, coordinar el acceso con Matías, propietario del repositorio.
2. Antes de actualizar la API, instalar y comprobar el backend desde la raíz del repo. `backend/requirements.txt` ya fija las versiones compatibles comprobadas. `.python-version` contiene 3.12.10; si existe `PYTHON_VERSION` en Render, tiene prioridad y debe coincidir.
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
5. Revisar el frontend local siguiendo `frontend/README.md`. **Ya está implementado, consume el contrato completo y su build funciona; todavía no se publicó.** La vista actual muestra todos los caudales y el déficit real.
6. Importar el mismo repositorio en Vercel siguiendo la sección siguiente. Vercel usa el JSON geométrico versionado y no necesita ejecutar Python.
7. Probar una simulación desde la página publicada, incluida la primera solicitud después de un periodo de inactividad. Guardar URLs reales y resultados verificados en el contexto; no dar por publicado un servicio solo por haberlo configurado.

## Importar el frontend en Vercel

La configuración está preparada en el repositorio; estos pasos todavía no se ejecutaron en una cuenta. Los efectos pedidos por el usuario ya están implementados y verificados localmente. Antes de desplegar, los cambios que se quieran publicar deben estar subidos a GitHub.

1. En el panel de Vercel, pulsar **Add New… → Project**.
2. En **Import Git Repository**, buscar el repositorio y pulsar **Import**. Si pertenece a una cuenta personal de GitHub, Vercel exige que lo importe su propietario: un colaborador no puede hacerlo desde su propia cuenta solo por habilitar la app. El propietario puede usar **Configure GitHub App** para autorizar ese repositorio si no aparece. En una organización se requiere ser miembro con permisos adecuados; un colaborador externo no basta. Si se usa un fork propio, hay que mantenerlo sincronizado.
3. En **Configure Project**, usar un nombre descriptivo, por ejemplo `infraestructura-red`.
4. En **Root Directory**, pulsar **Edit**, seleccionar `frontend` y confirmar. En **Framework Preset**, comprobar **Vite**.
5. En **Build and Output Settings**, comprobar los valores de `frontend/vercel.json`: instalación `npm ci`, build `npm run build`, salida `dist`. No usar comandos Python aquí.
6. En **Environment Variables**, agregar `VITE_API_URL` con valor `https://infraestructura-red-api.onrender.com`, sin `/api` ni barra final. No es un secreto: la dirección queda incluida en JavaScript. Incluir los entornos donde se vaya a probar la página.
7. Pulsar **Deploy**. `engines.node` del `package.json` establece **24.x**; comprobar la versión usada en los logs. También se puede consultar en **Settings → Build and Deployment → Node.js Version**.
8. Cuando termine, abrir la URL HTTPS y comprobar las vistas Tendidos/Capacidad, caudales, balance, selector y tabla. Repetir en móvil y tras inactividad de Render. Si falla, revisar la solicitud de red y los logs reales; no cambiar la API por datos simulados.
9. Compartir el origen definitivo con Matías para revisar CORS en FastAPI. Actualmente admite todos los orígenes sin credenciales; al restringirlo, contemplar las direcciones de producción, previews que se usen y desarrollo local.

Para la ampliación de casos/barrios, primero actualizar Render y verificar `POST /api/simular-red` con `caso_red: progresivo`, confirmación del caso y balances individuales. Luego probar selector y comparación desde el frontend y publicar su build. La API anterior puede ignorar el campo: la página lo detecta y no presenta otro caso como Progresivo. Resultado local de referencia: déficit 0/0/47.09 m³/día en Base/+10 %/+30 %. Ver [casos-capacidad.md](casos-capacidad.md).

Si cambia `VITE_API_URL`, generar un nuevo despliegue: no se modifica el bundle ya publicado. La aplicación actual no usa rutas de React Router, por lo que no se añadieron reglas de reescritura. Registrar la URL y qué se comprobó en `context.md` al finalizar.

## Referencias oficiales consultadas

- Vite en Vercel: https://vercel.com/docs/frameworks/frontend/vite
- Importar un proyecto Git: https://vercel.com/docs/getting-started-with-vercel/import
- Versiones Node en Vercel: https://vercel.com/docs/functions/runtimes/node-js/node-js-versions
- FastAPI en Vercel: https://vercel.com/docs/frameworks/backend/fastapi
- Runtime Python y empaquetado: https://vercel.com/docs/functions/runtimes/python
- FastAPI en Render: https://render.com/docs/deploy-fastapi
- Versión de Python en Render: https://render.com/docs/python-version
- Directorio raíz y monorepos en Render: https://render.com/docs/monorepo-support
- Limitaciones del plan gratuito de Render: https://render.com/docs/free
- Definición de VPS y responsabilidades: https://aws.amazon.com/what-is/vps/
- AWS Lambda: https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
