from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.routes_flujo import router as flujo_router
from backend.app.api.routes_modelo import router as modelo_router
from backend.app.api.routes_red import router as red_router

app = FastAPI(title="API Red de Agua")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flujo_router, prefix="/api")
app.include_router(modelo_router, prefix="/api")
app.include_router(red_router, prefix="/api")
