"""Funciones reutilizables para CreatorROI."""
from pathlib import Path
import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error


def evaluar_modelo(modelo, X_train, y_train, X_val, y_val):
    """Entrena un modelo y devuelve sus predicciones y errores en euros."""
    modelo.fit(X_train, y_train)
    predicciones_train = modelo.predict(X_train)
    predicciones = modelo.predict(X_val)
    mae_train = mean_absolute_error(y_train, predicciones_train)
    mae_val = mean_absolute_error(y_val, predicciones)
    print("MAE de entrenamiento:", round(mae_train, 2), "€")
    print("MAE de validación:", round(mae_val, 2), "€")
    print("Predicciones negativas:", (predicciones < 0).sum())
    return predicciones, mae_train, mae_val


def codificar_datos(datos, categorias, columnas=None):
    """Usa las categorías aprendidas en entrenamiento, incluso con una sola fila."""
    copia = datos.copy()
    for columna, valores in categorias.items():
        if copia[columna].isna().any() or not copia[columna].isin(valores).all():
            raise ValueError("Categoría vacía o desconocida en " + columna)
        copia[columna] = pd.Categorical(copia[columna], categories=valores)
    resultado = pd.get_dummies(copia, columns=list(categorias), drop_first=True)
    if columnas is not None:
        resultado = resultado.reindex(columns=columnas, fill_value=0)
    return resultado


def guardar_modelo(paquete, ruta):
    """Guarda el modelo junto con los elementos necesarios para reutilizarlo."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(paquete, ruta, compress=3)


def predecir_tarifas(datos, paquete):
    """Prepara nuevas filas igual que el entrenamiento y estima sus tarifas."""
    entrada = datos[paquete["variables"]].copy()
    codificados = codificar_datos(entrada, paquete["categorias"], paquete["columnas"])
    escalados = paquete["scaler"].transform(codificados)
    return paquete["modelo"].predict(escalados)
