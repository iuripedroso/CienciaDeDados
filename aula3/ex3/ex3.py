import pandas as pd

df = pd.read_csv(
    'log_sistema.csv',
    skiprows=2,
    nrows=2,
    engine='python'
)

print(df)