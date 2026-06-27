# 📊Insurance Solvency & Profitability Tracker

Pipeline en Python que descarga periódicamente las estadísticas trimestrales públicas de **EIOPA** (regulador europeo de seguros), extrae el **ratio de solvencia (Solvencia II)** y el **Combined Ratio** de los principales mercados aseguradores europeos, los consolida en un histórico en Excel sin duplicar registros, y los visualiza en un dashboard de Power BI.

## 🚀 Objetivos del proyecto

- Descarga las estadísticas Solo/Quarterly de EIOPA: *Own Funds* (fondos propios y SCR) y *Premiums, Claims and Expenses* (primas, siniestros y gastos)
- Extrae el **ratio de solvencia** (`R0620` — Ratio of Eligible own funds to SCR), por país y por ramo (Vida / No-Vida / Todas)
- Extrae el **Combined Ratio** y el **Expense Ratio** (`Z0001`, `Z0002`), métricas de rentabilidad técnica del ramo No-Vida
- Cubre 5 mercados europeos: España, Alemania, Francia, Italia e Irlanda
- **Anti-duplicados y gestión de revisiones**: por cada trimestre y país, si el dato ya existe se actualiza con el valor más reciente (EIOPA revisa datos históricos en cada publicación); si no existe, se añade
- Ejecución manual — los datos de EIOPA se publican trimestralmente, no tiene sentido automatizar una ejecución diaria
- Histórico consolidado en Excel, listo para conectar con Power BI

## 🛠️ Estructura del repositorio

| Archivo | Descripción |
|---|---|
| `tracker.py` | Script principal: descarga, procesa y actualiza el histórico |
| `tracker.ipynb` | Notebook de desarrollo y exploración |
| `solvencia_rentabilidad.xlsx` | Histórico de ratios desde 2016 Q3 |
| `dashboard.pbix` | Dashboard Power BI (Solvencia + Rentabilidad técnica) |

## Dashboard Power BI

El `.pbix` conecta directamente con el Excel histórico y muestra dos vistas:

**Página 1 — Solvencia**
Evolución del ratio de solvencia por país y ramo, con línea de referencia en el mínimo regulatorio (1,0 / 100%) y comparativa entre los 5 mercados.

**Página 2 — Rentabilidad técnica**
Evolución del Combined Ratio (No-Vida) por país, con línea de breakeven en 1,0 — por debajo, el negocio asegurador es rentable; por encima, pierde dinero asegurando (compensándolo, si puede, con resultado financiero).

## 📂 Fuente de datos

[EIOPA — Insurance Statistics](https://www.eiopa.europa.eu/tools-and-data/insurance-statistics_en), datos Solo/Quarterly, sección *Own Funds* y *Premiums, Claims and Expenses*. Ambos ratios (solvencia y combined ratio) vienen ya calculados por EIOPA — el script solo filtra, pivota y consolida el histórico.

## 🛠️ Stack

Python 3.12 · pandas · requests · openpyxl · Excel · Power BI

## 🚀 Uso rápido

Instala las dependencias:

```
pip install requests pandas openpyxl
```

Edita la ruta del Excel histórico en `tracker.py`:

```python
ARCHIVO_HISTORICO = r"C:\tu\ruta\solvencia_rentabilidad.xlsx"
```

Ejecuta el script cuando quieras comprobar si EIOPA ha publicado un trimestre nuevo:

```
python tracker.py
```

## 📌 Notas

- EIOPA publica los datos de un trimestre con varias semanas de retraso respecto al cierre del trimestre, y los revisa en publicaciones posteriores — el script gestiona esas revisiones automáticamente.
- El Combined Ratio y el Expense Ratio solo existen para el ramo No-Vida (no aplican a Vida).
- Si mueves el Excel de ubicación, actualiza la ruta tanto en `tracker.py` como en el origen de datos del `.pbix`.
- Países y ramos cubiertos son configurables editando las listas `PAISES` en `tracker.py`.
