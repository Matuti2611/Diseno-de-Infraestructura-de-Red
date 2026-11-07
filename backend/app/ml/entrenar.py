import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# 1. Cargar los datos generados por tu compañero
# Ajustá la ruta según desde dónde ejecutes el script
df = pd.read_csv('backend/data/raw/historial_consumo.csv')
# 2. Preprocesamiento (Features)
# Sacamos el ID porque no tiene valor predictivo y separamos la variable objetivo a predecir
X = df.drop(columns=['nodo_id', 'consumo_futuro'])
y = df['consumo_futuro']

# Convertimos la variable categórica tipo_zona en columnas numéricas (One-Hot Encoding)
X = pd.get_dummies(X, columns=['tipo_zona'], drop_first=True)

# 3. Separar en entrenamiento (80%) y prueba (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Definir los modelos a comparar
modelos = {
    "Regresión Lineal": LinearRegression(),
    "Árbol de Decisión": DecisionTreeRegressor(random_state=42)
}

# 5. Entrenar y evaluar
for nombre, modelo in modelos.items():
    # Entrenar el modelo con el 80% de los datos
    modelo.fit(X_train, y_train)
    
    # Predecir sobre el 20% de prueba
    predicciones = modelo.predict(X_test)
    
    # Calcular métricas solicitadas
    mae = mean_absolute_error(y_test, predicciones)
    rmse = np.sqrt(mean_squared_error(y_test, predicciones))
    r2 = r2_score(y_test, predicciones)
    
    print(f"--- {nombre} ---")
    print(f"MAE:  {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R²:   {r2:.4f}\n")