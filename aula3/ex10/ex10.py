import pandas as pd

iterador_blocos = pd.read_csv('transacoes_grandes.csv', sep=';', chunksize=20)

for i, bloco in enumerate(iterador_blocos, start=1):
    print(f"--- Bloco {i} ---")
    print(f"Número de linhas no bloco: {len(bloco)}")
    print("Três primeiras linhas:")
    print(bloco.head(3))
    print("-" * 30, "\n")