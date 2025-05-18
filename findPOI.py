import pandas as pd

# === Leer archivo con códigos y descripciones ===
POI2_csv = './POI_Size.csv'
df_facilities = pd.read_csv(POI2_csv)

# Lista de códigos para verificación (opcional)
EL = list(df_facilities['Facility Code'].astype(int))

# === Leer archivo POI ===
num = int(input("Archivo POI (7 números): "))
POI_csv = f'./POIs/POI_{num}.csv'
df_pois = pd.read_csv(POI_csv)

# Verificación de coincidencias
FT = df_pois['FAC_TYPE']
Coincide = sum(int(j) in EL for j in FT)
Not_finded = len(FT) - Coincide

print(f"Coincidencias: {Coincide}")
print(f"No encontrados: {Not_finded}")

# === Unir los datos por FAC_TYPE y Facility Code ===
merged = pd.merge(
    df_pois,
    df_facilities,
    how='left',
    left_on='FAC_TYPE',
    right_on='Facility Code'
)

# === Crear nuevo DataFrame con solo columnas deseadas ===
NWPOI = merged[['LINK_ID', 'FAC_TYPE', 'Facility Description', 'Size']]

# === Guardar archivo final ===
output_file = f'Check_{num}.csv'
NWPOI.to_csv(output_file, index=False)
print(f"Archivo guardado como {output_file}")