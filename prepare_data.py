"""
Extrae del zip de DRIAMS los datos CRUDOS de Staphylococcus aureus.

No filtra por etiqueta ni codifica nada. Toda la limpieza se hace en el notebook,
a la vista. Este script solo evita que el notebook dependa de un zip de 8,9 GB.

Requiere:  data/driams.zip   (kaggle datasets download drscarlat/driams -p data/)
Produce:   data/saureus_raw.csv   6.994 x 98   metadata cruda, una fila por muestra
           data/saureus_raw.npy   6.994 x 6000 espectros, filas alineadas al csv

Uso:  python prepare_data.py
"""
import io
import os
import zipfile

import numpy as np
import pandas as pd

ZIP = "data/driams.zip"
ESPECIE = "Staphylococcus aureus"
ANIOS = ["2015", "2016", "2017", "2018"]
N_BINS = 6000
COLS_STRAT = ["code", "acquisition_date", "acquisition_time", "workstation", "patient_no", "case_no"]

if not os.path.exists(ZIP):
    raise SystemExit(f"falta {ZIP}. Corre: kaggle datasets download drscarlat/driams -p data/")

z = zipfile.ZipFile(ZIP)
leer = lambda ruta: pd.read_csv(io.BytesIO(z.read(ruta)), low_memory=False)

# metadata de los cuatro anios de DRIAMS-A, sin tocar las columnas de antibioticos
clean = pd.concat([leer(f"DRIAMS-A/id/{y}/{y}_clean.csv").assign(year=y) for y in ANIOS],
                  ignore_index=True)
strat = pd.concat([leer(f"DRIAMS-A/id/{y}/{y}_strat.csv")[COLS_STRAT] for y in ANIOS],
                  ignore_index=True)

crudo = clean[clean.species == ESPECIE].merge(strat, on="code", how="left")
assert not crudo.code.duplicated().any(), "hay codes duplicados"
print(f"{ESPECIE}: {len(crudo)} muestras de {len(clean)} en DRIAMS-A")

# espectros en el mismo orden que las filas del csv
X = np.empty((len(crudo), N_BINS), dtype=np.float32)
for i, (code, year) in enumerate(zip(crudo.code, crudo.year)):
    with z.open(f"DRIAMS-A/binned_6000/{year}/{code}.txt") as f:
        a = np.loadtxt(f, skiprows=1, dtype=np.float32)
    assert a.shape == (N_BINS, 2), f"{code}: se esperaban {N_BINS} bins, hay {a.shape[0]}"
    X[i] = a[:, 1]

crudo.to_csv("data/saureus_raw.csv", index=False)
np.save("data/saureus_raw.npy", X)
print(f"data/saureus_raw.csv  {crudo.shape}")
print(f"data/saureus_raw.npy  {X.shape}  ({X.nbytes/1e6:.0f} MB)")
