import pandas as pd

df = pd.read_csv(
    'transacoes.csv',
    sep=';',
    thousands='.',
    decimal=','
)

print(df)
print(df.dtypes)