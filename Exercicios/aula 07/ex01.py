import pandas as pd

# Lendo o CSV com configurações específicas
df = pd.read_csv(
    'vendas.csv',
    header=None,      # não possui cabeçalho
    index_col=0,      # primeira coluna como índice
    na_values='ND'    # trata "ND" como valor ausente
)

# Exibindo o DataFrame
print(df)