import warnings
import joblib
from backend.app.config import RUTA_MODELO
from backend.app.ml.features import preparar_features_inferencia

warnings.filterwarnings("ignore")
modelo = joblib.load(RUTA_MODELO)

def predecir_demanda(df_zonas, multiplicador_escenario):
    df_sim = df_zonas.copy()
    df_sim['crecimiento_poblacional_estimado'] *= multiplicador_escenario
    
    columnas_esperadas = list(getattr(modelo, "feature_names_in_", []))
    X = preparar_features_inferencia(df_sim, columnas_esperadas)
    
    return modelo.predict(X)
