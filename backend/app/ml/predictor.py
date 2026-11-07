import joblib
import pandas as pd
import warnings
from backend.app.config import RUTA_MODELO

warnings.filterwarnings("ignore")
modelo = joblib.load(RUTA_MODELO)

def predecir_demanda(df_zonas, multiplicador_escenario):
    """Aplica el escenario, prepara los datos y devuelve las predicciones."""
    df_sim = df_zonas.copy()
    df_sim['crecimiento_poblacional_estimado'] *= multiplicador_escenario
    
    X = df_sim.drop(columns=['nodo_id'])
    X = pd.get_dummies(X, columns=['tipo_zona'], drop_first=True)
    X = X.reindex(columns=modelo.feature_names_in_, fill_value=0)
    
    return modelo.predict(X)