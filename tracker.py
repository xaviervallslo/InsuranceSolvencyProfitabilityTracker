# %%
# Solvency & Profitability Tracker — Sector Asegurador (Solvencia II)
#
# Descarga las estadísticas trimestrales públicas de EIOPA (regulador europeo
# de seguros), extrae el ratio de solvencia (SCR ratio) y el Combined Ratio,
# y actualiza un histórico en Excel sin duplicar ni perder revisiones de
# trimestres ya publicados.
#
# Fuente: https://www.eiopa.europa.eu/tools-and-data/insurance-statistics_en
#
# Ejecución: manual, cuando quieras comprobar si EIOPA ha publicado un
# trimestre nuevo (normalmente cada 3 meses).

import pandas as pd
import requests
from io import StringIO
import os

# %%
# --- Configuración ---

# URLs oficiales de EIOPA (sección "Own funds" y "Premiums, claims and
# expenses", entidad Solo, frecuencia Quarterly)
URL_OWN_FUNDS = "https://nexteuropa-multisites.s3.eu-west-1.amazonaws.com/www.eiopa.europa.eu/assets/insurance-statistics/SQ_Own_Funds.csv"
URL_PREMIUMS  = "https://nexteuropa-multisites.s3.eu-west-1.amazonaws.com/www.eiopa.europa.eu/assets/insurance-statistics/SQ_Premiums_Claims_Expenses.csv"

# Países a trackear (tal y como aparecen en el dataset de EIOPA, en mayúsculas)
PAISES = ["SPAIN", "GERMANY", "FRANCE", "ITALY", "IRELAND"]

# Fichero histórico de salida — RUTA ABSOLUTA, edítala antes de ejecutar
ARCHIVO_HISTORICO = r"C:\Users\TU_USUARIO\OneDrive\insurance-solvency-tracker\solvencia_rentabilidad.xlsx"


# %%
# --- 1. Descarga de los ficheros fuente ---

def descargar_csv(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return pd.read_csv(StringIO(resp.text))

df_own_funds = descargar_csv(URL_OWN_FUNDS)
df_premiums  = descargar_csv(URL_PREMIUMS)

print("Own Funds:", df_own_funds.shape)
print("Premiums/Claims/Expenses:", df_premiums.shape)


# %%
# --- 2. Ratio de solvencia (SCR ratio) ---
# Código de partida R0620 = "Ratio of Eligible own funds to SCR", ya
# calculado por EIOPA. Lo separamos por tipo de negocio (Vida/No-Vida/Todas).

df_solv = df_own_funds[
    (df_own_funds['Item code'] == 'R0620') &
    (df_own_funds['Reporting country'].isin(PAISES))
]

pivot_solv = df_solv.pivot_table(
    index=['Reporting country', 'Reference period'],
    columns='Undertaking type',
    values='Value'
).reset_index()

pivot_solv = pivot_solv[['Reporting country', 'Reference period',
                         'All undertaking types', 'Life undertakings', 'Non-Life undertakings']]
pivot_solv.columns = ['Pais', 'Trimestre',
                       'Ratio_Solvencia_Todas', 'Ratio_Solvencia_Vida', 'Ratio_Solvencia_NoVida']


# %%
# --- 3. Combined Ratio y Expense Ratio (rentabilidad técnica, solo No-Vida) ---
# Códigos Z0001 (Net Combined Ratio) y Z0002 (Net Expense Ratio), también ya
# calculados por EIOPA. Solo existen para el ramo No-Vida.

df_cr = df_premiums[
    (df_premiums['Item code'].isin(['Z0001', 'Z0002'])) &
    (df_premiums['Reporting country'].isin(PAISES))
]

pivot_cr = df_cr.pivot_table(
    index=['Reporting country', 'Reference period'],
    columns='Item',
    values='Value'
).reset_index()

pivot_cr.columns = ['Pais', 'Trimestre', 'Combined_Ratio_NoVida', 'Expense_Ratio_NoVida']


# %%
# --- 4. Unión de ambas fuentes en una sola tabla ---

df_final = pivot_solv.merge(pivot_cr, on=['Pais', 'Trimestre'], how='outer')
df_final = df_final.sort_values(['Pais', 'Trimestre']).reset_index(drop=True)

print("Filas procesadas en esta ejecución:", df_final.shape[0])


# %%
# --- 5. Actualizar histórico (altas nuevas + revisiones), sin duplicar ---
# Clave única = (Pais, Trimestre). Si el trimestre no existe en el histórico,
# se añade. Si ya existe pero EIOPA ha revisado el valor (sucede con
# frecuencia en datos regulatorios), se actualiza con el valor más reciente.

if os.path.exists(ARCHIVO_HISTORICO):
    df_historico = pd.read_excel(ARCHIVO_HISTORICO)
else:
    df_historico = pd.DataFrame(columns=df_final.columns)

CLAVE = ['Pais', 'Trimestre']

# pd.concat + drop_duplicates(keep='last') -> el dato nuevo (df_final) siempre
# gana sobre el histórico para la misma clave: añade lo que falta y corrige
# lo que EIOPA haya revisado.
df_actualizado = pd.concat([df_historico, df_final]).drop_duplicates(subset=CLAVE, keep='last')
df_actualizado = df_actualizado.sort_values(CLAVE).reset_index(drop=True)

print(f"Registros en histórico antes:   {len(df_historico)}")
print(f"Registros en histórico después: {len(df_actualizado)}")

df_actualizado.to_excel(ARCHIVO_HISTORICO, index=False)
print(f"\nGuardado en: {ARCHIVO_HISTORICO}")
