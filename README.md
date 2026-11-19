<img src="banner.png" alt="Predicción de resistencia a oxacilina desde espectros MALDI-TOF" width="100%">

# Predicción de resistencia a oxacilina en *Staphylococcus aureus* desde espectros MALDI-TOF

Proyecto final de **Inteligencia Artificial I**, 2026-2 · Universidad Industrial de Santander

## Objetivo

Predecir si una cepa de *Staphylococcus aureus* es resistente a la oxacilina —es decir, si es
MRSA— usando únicamente su espectro de masas MALDI-TOF, sin esperar el antibiograma por cultivo.

Hoy el laboratorio identifica la especie en minutos con MALDI-TOF, pero determinar la resistencia
toma de 24 a 72 horas de cultivo. Durante esas horas el paciente recibe antibióticos de amplio
espectro elegidos a ciegas, y ese uso es uno de los motores de la resistencia que se quiere
contener.

La hipótesis tiene sustento biológico: la resistencia a oxacilina la confiere el gen `mecA`, que
codifica la proteína PBP2a y viaja en el cassette SCC*mec*. Ese cassette altera el proteoma, y el
proteoma es justamente lo que mide MALDI-TOF. Si la señal está en el espectro, la resistencia se
estima en los mismos minutos que la identificación, sin insumos adicionales.

## Dataset

**DRIAMS** — *Database of Resistance Information on Antimicrobials and MALDI-TOF Mass Spectra*

- Descarga: https://www.kaggle.com/datasets/drscarlat/driams
- Artículo: [Weis et al., *Nature Medicine* (2022)](https://doi.org/10.1038/s41591-021-01619-9)

| | |
|---|---|
| Sitio usado | DRIAMS-A, Hospital Universitario de Basilea, 2015-2018 |
| Muestras de *S. aureus* | 6.994 |
| Con antibiograma de oxacilina | **3.790**, de 1.841 pacientes |
| Balance | 726 resistentes (19,2%), 3.064 susceptibles |
| Variables | 6.000 bins de intensidad entre 2.000 y 20.000 Da |

## Integrantes

| Nombre | Código |
|---|---|
| Juan David Lipez Guevara | 2223102 |

## Video

<!-- PENDIENTE: reemplazar por la URL de YouTube -->
`PENDIENTE`

## Estructura

```
├── mrsa_maldi_tof.ipynb    notebook acumulativo, las tres entregas
├── diapositivas.pdf        resumen del semestre
├── banner.png
├── prepare_data.py         extrae del zip de DRIAMS los datos de S. aureus
└── requirements.txt
```

El notebook recorre las tres entregas en orden:

| Secciones | Contenido |
|---|---|
| 1 a 10 | Motivación, dataset, limpieza, EDA, detección de outliers |
| 11 a 19 | Particionado por paciente, DecisionTree, RandomForest, SVM, CrossValidation, perceptrón multicapa, comparación |
| 20 a 24 | Escalado, PCA, KMeans, DBSCAN |

## Resultados

Partición 80/20 **por paciente**, no por espectro: el 74% de los espectros provienen de pacientes
con más de una muestra, así que repartirlos al azar deja al mismo paciente en entrenamiento y
prueba y el modelo acierta reconociéndolo. Evaluación sobre 732 espectros nunca vistos, de los
cuales 139 son resistentes.

| Modelo | accuracy | tpr | tnr | Resistentes hallados |
|---|---|---|---|---|
| DecisionTree (`max_depth=5`) | 0,829 | **0,626** | 0,877 | **87** de 139 |
| RandomForest (`n_estimators=5`) | 0,833 | 0,338 | 0,949 | 47 de 139 |
| SVM (`kernel=linear`) | 0,842 | 0,554 | 0,909 | 77 de 139 |
| Red neuronal (10 capas, 100 epochs) | **0,884** | 0,540 | **0,965** | 75 de 139 |

El baseline de clase mayoritaria —contestar *susceptible* siempre— da 0,810 de accuracy con
`tpr = 0`. Por eso se reportan las tres métricas: `tpr` es la proporción de resistentes detectados
y `tnr` la de susceptibles.

**El orden se invierte entre métricas.** La red gana en accuracy y el árbol la pierde, pero el
árbol encuentra 87 resistentes y la red 75. En un hospital el error caro es no detectar un MRSA,
así que el `tpr` pesa más que la accuracy.

**El clustering no encuentra la resistencia.** Proyectando a 2 componentes con PCA —que solo
recogen el 17,6% de la varianza— KMeans parte el conjunto en dos grupos con 14,9% y 23,7% de
resistentes, contra un 19,2% general: no separa la clase. DBSCAN ve una sola nube.

Eso no contradice los resultados supervisados, los explica: la señal de resistencia existe, pero
**no es la variación dominante del espectro**, y por eso el problema necesita aprendizaje
supervisado.

## Reproducir

```bash
pip install -r requirements.txt
kaggle datasets download drscarlat/driams -p data/
python prepare_data.py
```

`prepare_data.py` extrae del zip las 6.994 muestras de *S. aureus* y produce `data/saureus_raw.csv`
y `data/saureus_raw.npy`, que son los dos archivos que lee el notebook. Los datos no están en el
repositorio porque el zip pesa 8,2 GB.

Para correr en Colab, basta subir esos dos archivos a Drive: la primera celda detecta el entorno y
monta la unidad automáticamente.
