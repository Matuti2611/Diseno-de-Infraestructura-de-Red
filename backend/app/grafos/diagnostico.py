from backend.app.config import UMBRAL_SATURACION

def obtener_estados_flujo(mst, dict_flujos):
    """
    Calcula el estado de flujo (magnitud neta no negativa) para TODOS los tendidos del MST.
    Identifica si está saturada al 100% (con tolerancia numérica).
    """
    estados = []
    for u, v, datos in mst.edges(data=True):
        capacidad_max = float(datos['capacidad_m3_dia'])
        
        f_uv = dict_flujos.get(u, {}).get(v, 0)
        f_vu = dict_flujos.get(v, {}).get(u, 0)
        flujo_neto = max(0.0, float(max(f_uv, f_vu)))
        
        saturada = bool(flujo_neto >= (capacidad_max - 1e-5))
        porcentaje_uso = (flujo_neto / capacidad_max * 100.0) if capacidad_max > 0 else 0.0
        
        estados.append({
            "origen": u,
            "destino": v,
            "flujo_actual": round(flujo_neto, 2),
            "capacidad_maxima": round(capacidad_max, 2),
            "saturada": saturada,
            "porcentaje_uso": round(porcentaje_uso, 2)
        })
    return estados

def obtener_aristas_saturadas(mst, dict_flujos):
    """Filtra aristas que superan el UMBRAL_SATURACION (ej. >= 90%)."""
    todos = obtener_estados_flujo(mst, dict_flujos)
    return [
        {
            "origen": e["origen"],
            "destino": e["destino"],
            "flujo": e["flujo_actual"],
            "capacidad": e["capacidad_maxima"],
            "uso_pct": e["porcentaje_uso"]
        }
        for e in todos if e["porcentaje_uso"] >= UMBRAL_SATURACION
    ]
