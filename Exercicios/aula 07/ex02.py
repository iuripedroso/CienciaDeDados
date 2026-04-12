import pandas as pd

# Supondo que o DataFrame já existe
# relatorio_anual = ...

# 1️⃣ Salvar o DataFrame em Excel na aba "Resultados"
relatorio_anual.to_excel(
    'relatorio.xlsx',
    sheet_name='Resultados',
    index=False  # opcional: não salvar o índice
)

# 2️⃣ Ler apenas a aba "Dados Brutos" de um Excel existente
df_dados_brutos = pd.read_excel(
    'relatorio.xlsx',   # ou outro arquivo existente
    sheet_name='Dados Brutos'
)

# Exibir para conferir
print(df_dados_brutos)