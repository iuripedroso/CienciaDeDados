import pandas as pd

df = pd.read_csv(
    'sensores.csv',
    sep=',',
    na_values=['NA', '-']
)

print(df.info())
print(df.head(20))