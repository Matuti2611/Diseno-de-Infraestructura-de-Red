from backend.app.config import UMBRAL_SATURACION

def obtener_aristas_saturadas(mst, dict_flujos):
    saturadas = []
    for u, v, datos in mst.edges(data=True):
        capacidad_max = datos['capacidad_m3_dia']
        
        flujo_neto = abs(dict_flujos[u].get(v, 0))
        porcentaje_uso = (flujo_neto / capacidad_max) * 100
        
        if porcentaje_uso >= UMBRAL_SATURACION:
            saturadas.append({
                "origen": u, "destino": v, 
                "flujo": flujo_neto, "capacidad": capacidad_max, 
                "uso_pct": porcentaje_uso
            })
    return saturadas