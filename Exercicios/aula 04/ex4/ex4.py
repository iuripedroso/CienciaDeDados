import pandas as pd

df = pd.read_csv(
    'estoque.csv',
    sep=';',
    decimal=','
)

print(df.dtypes)