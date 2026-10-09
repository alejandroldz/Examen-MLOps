import csv
from pathlib import Path
import joblib
from .contracts import Entrada, Salida
import pandas as pd


def leer_csv(ruta: Path) -> list[Entrada]:
    # TODO
    rows=[]
    try:
        csv = pd.read_csv(ruta)
        if csv.shape[0] == 0:
            raise ValueError("Archivo vacío, sin filas")
    except:
        raise ValueError("Archivo vacío o no existe")
    
    for i, row in csv.iterrows():
        cleaned_row = Entrada.model_validate(row.to_dict())
        rows.append(cleaned_row)
    
    return rows


def preprocesar(entrada: Entrada) -> list[float]:
    # TODO
    return [
        round(entrada.peso_kg, 1),
        round(entrada.distancia_km, 1)
    ]


def cargar_modelo(ruta: Path):
    # TODO
    model = joblib.load(ruta)
    return model


def predecir(entrada: Entrada, modelo) -> Salida:
    # TODO
    row = preprocesar(entrada)
    probs = modelo.predict_proba([row])
    if probs[0][0] < probs[0][1]:
        categoria = "urgente"
        confianza = probs[0][1]
    else:
        categoria = "normal"
        confianza = probs[0][0]
    d = {
       "id_paquete":entrada.id_paquete,
       "categoria":categoria,
       "confianza":confianza
    }
    salida = Salida.model_validate(d)
    return salida

def guardar_csv(resultados: list[Salida], ruta: Path) -> None:
    l = []
    for i in resultados:
        l.append(dict(i))

    df = pd.DataFrame(l)
    if Path(ruta).exists():
        return
    df.to_csv(ruta, index=False)


def ejecutar(entrada: Path, modelo: Path, salida: Path) -> None:
    # TODO
    csv = leer_csv(entrada)
    modelo = cargar_modelo(modelo)
    
    resultados = []
    try:
        for row in csv:
            resultados.append(predecir(entrada=row,modelo=modelo))
    except:
        raise
    guardar_csv(resultados=resultados, ruta=salida)


if __name__ == "__main__":
    ejecutar(
        Path("data/raw/paquetes.csv"),
        Path("models/modelo.joblib"),
        Path("resultados.csv"),
    )
