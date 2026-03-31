import pandas as pd

df = pd.read_csv(
    'clima.csv',
    sep=',',
    encoding='utf-8',
    parse_dates=['data'],
    index_col='data',
    usecols=['data', 'temperatura_c', 'umidade_relativa'],
    dtype={
        'temperatura':'float64',
        'umidade':'int64'
    },
    decimal=','
)

print(df.info())
print (df)