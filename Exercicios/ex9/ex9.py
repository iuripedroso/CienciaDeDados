import pandas as pd

df = pd.read_csv('notas.csv', sep=',')

print("--- Estatísticas Descritivas ---")
print(df.describe())

print("\n--- Média de cada disciplina isolada ---")
print(df[['matematica', 'portugues', 'historia']].mean())