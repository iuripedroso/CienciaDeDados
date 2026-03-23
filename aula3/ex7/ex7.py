import pandas as pd

df = pd.read_csv('experimento.csv', sep=',')

print("--- Visão Inicial (head) ---")
print(df.head())

print("\n--- Visão Final (tail) ---")
print(df.tail())

print("\n--- Resumo Estatístico (describe) ---")
print(df.describe())