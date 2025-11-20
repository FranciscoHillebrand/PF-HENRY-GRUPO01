# ETL LIMPIEZA Y TRANSFORMACIÓN CSV por separado, hay que modificar el nombre del archivo y de las columnas a eliminar y a cambiar el tipo de dato

import pandas as pd

# --- 1 Cargar archivo CSV ---
ruta = "C:/Users/ferna/OneDrive/SoyHenry/Proyecto final/Dataset_NBA/common_player_info.csv"
df = pd.read_csv(ruta)

print(f"Archivo cargado: {df.shape[0]} filas y {df.shape[1]} columnas\n")

# --- 2 Eliminar columnas innecesarias ---
#  Cambia los nombres de las columnas que quieras eliminar
columnas_a_eliminar = ['first_name','last_name','display_last_comma_first','display_fi_last','player_slug', 'birthdate','school', 'country', 'season_exp', 'jersey', 'rosterstatus', 'games_played_current_season_flag', 'team_id', 'team_name', 'team_abbreviation', 'team_city', 'playercode', 'from_year', 'to_year', 'dleague_flag', 'nba_flag', 'games_played_flag', 'draft_round', 'draft_number', 'greatest_75_flag'] # ejemplo
df.drop(columns=columnas_a_eliminar, inplace=True, errors='ignore')

print(f"Columnas eliminadas: {columnas_a_eliminar}\n")

# --- 3 Verificar tipos de datos actuales ---
print("Tipos de datos antes de conversión:\n")
print(df.dtypes)
print("\n")

# --- 4 Cambiar tipo de dato de columnas específicas ---
#  Define aquí qué columnas querés cambiar y a qué tipo
# tipos posibles: 'int', 'float', 'str', 'datetime64[ns]'
conversion_tipos = {'person_id': 'object'
    }

for col, tipo in conversion_tipos.items():
    if col in df.columns:
        try:
            df[col] = df[col].astype(tipo)
            print(f"Columna '{col}' convertida a tipo {tipo}")
        except Exception as e:
            print(f"No se pudo convertir '{col}' a {tipo}: {e}")

print("\n Tipos de datos luego de conversión:\n")
print(df.dtypes)
print("\n")

# --- 5 Revisar nulos por columna ---
print("Cantidad de valores nulos por columna:\n")
print(df.isna().sum())
print("\n")

# --- 6 Eliminar filas con nulos ---
filas_antes = df.shape[0]
df.dropna(inplace=True)
filas_despues = df.shape[0]
print(f"Filas eliminadas por contener nulos: {filas_antes - filas_despues}")
print(f"Total de filas restantes: {filas_despues}\n")

# --- 7 Guardar el archivo limpio ---
salida = "C:/Users/ferna/OneDrive/SoyHenry/Proyecto final/Dataset_NBA/clean_common_player_info.csv"
df.to_csv(salida, index=False)
print(f"Archivo limpio guardado en:\n{salida}")
