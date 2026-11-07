import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

df = pd.read_csv('backend/data/raw/historial_consumo.csv')

X = df.drop(columns=['nodo_id', 'consumo_futuro'])
y = df['consumo_futuro']

X = pd.get_dummies(X, columns=['tipo_zona'], drop_first=True)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelos = {
    "Regresión Lineal": LinearRegression(),
    "Árbol de Decisión": DecisionTreeRegressor(random_state=42)
}

for nombre, modelo in modelos.items():
    modelo.fit(X_train, y_train)
    
    predicciones = modelo.predict(X_test)
    
    mae = mean_absolute_error(y_test, predicciones)
    rmse = np.sqrt(mean_squared_error(y_test, predicciones))
    r2 = r2_score(y_test, predicciones)
    
    print(f"--- {nombre} ---")
    print(f"MAE:  {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R²:   {r2:.4f}\n")

os.makedirs('backend/models', exist_ok=True)

mejor_modelo = modelos["Regresión Lineal"]
joblib.dump(mejor_modelo, 'backend/models/modelo_consumo.joblib')

print("Modelo de Regresión Lineal guardado exitosamente en backend/models/modelo_consumo.joblib")