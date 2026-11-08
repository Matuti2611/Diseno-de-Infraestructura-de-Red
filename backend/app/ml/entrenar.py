import os
import json
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from backend.app.config import RUTA_HISTORIAL, RUTA_MODELO, RUTA_METRICAS
from backend.app.data.cargar import cargar_historial
from backend.app.ml.features import preparar_features_entrenamiento
from backend.app.ml.evaluar import evaluar_modelo, imprimir_reporte_evaluacion

df = cargar_historial(RUTA_HISTORIAL)
X, y = preparar_features_entrenamiento(df)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelos = {
    "Regresión Lineal": LinearRegression(),
    "Árbol de Decisión": DecisionTreeRegressor(random_state=42)
}

metricas_dict = {}

for nombre, modelo in modelos.items():
    modelo.fit(X_train, y_train)
    predicciones = modelo.predict(X_test)
    
    metricas = evaluar_modelo(y_test, predicciones)
    metricas_dict[nombre] = metricas
    imprimir_reporte_evaluacion(nombre, y_test, predicciones)

os.makedirs('backend/models', exist_ok=True)

mejor_modelo = modelos["Regresión Lineal"]
joblib.dump(mejor_modelo, RUTA_MODELO)

with open(RUTA_METRICAS, 'w', encoding='utf-8') as f:
    json.dump(metricas_dict["Regresión Lineal"], f, indent=2)

print(f"Modelo guardado en {RUTA_MODELO}")
print(f"Métricas guardadas en {RUTA_METRICAS}")
