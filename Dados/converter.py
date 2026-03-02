# converter.py
import pandas as pd
import os

excel_path = 'Fini_analise.xlsx'   # arquivo está dentro da pasta Dados
json_path = 'fini_data.json'

if not os.path.exists(excel_path):
    raise FileNotFoundError(f"Arquivo não encontrado: {excel_path} no diretório {os.getcwd()}")

print("Lendo Excel:", excel_path)
df = pd.read_excel(excel_path, engine='openpyxl')

# Converter Emissão para string ISO (YYYY-MM-DD) para facilitar o JS
if 'Emissão' in df.columns:
    df['Emissão'] = pd.to_datetime(df['Emissão'], errors='coerce')
    df['Emissão'] = df['Emissão'].dt.strftime('%Y-%m-%d')

# Substituir NaN por None para JSON mais limpo
df = df.where(pd.notnull(df), None)

print("Gerando JSON:", json_path)
df.to_json(json_path, orient='records', force_ascii=False, indent=2)
print("JSON gerado em:", os.path.join(os.getcwd(), json_path))