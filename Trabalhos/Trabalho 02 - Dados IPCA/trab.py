import requests
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import datetime

url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)

    df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
    df['valor'] = pd.to_numeric(df['valor'])

    ano_atual = datetime.datetime.now().year
    df_filtrado = df[df['data'].dt.year >= (ano_atual - 10)].copy()

    media = df_filtrado['valor'].mean()
    maximo = df_filtrado['valor'].max()
    minimo = df_filtrado['valor'].min()

    print("--- Estatísticas da Inflação (IPCA) nos últimos 10 anos ---")
    print(f"Média Mensal: {media:.2f}%")
    print(f"Máximo Mensal: {maximo:.2f}%")
    print(f"Mínimo Mensal: {minimo:.2f}%")
    print("---------------------------------------------------------")


    quantidade_linhas = len(df_filtrado)
    print(f"Total de registros salvos no banco: {quantidade_linhas} linhas")

    engine = create_engine('sqlite:///banco_dados_ipca.db', echo=False)
    df_filtrado.to_sql('ipca_mensal', con=engine, if_exists='replace', index=False)
    print("Dados salvos no banco de dados SQLite com sucesso.")
    engine = create_engine('sqlite:///banco_dados_ipca.db', echo=False)
    df_filtrado.to_sql('ipca_mensal', con=engine, if_exists='replace', index=False)
    print("Dados salvos no banco de dados SQLite com sucesso.")

    df_filtrado['Ano'] = df_filtrado['data'].dt.year
    df_agrupado_ano = df_filtrado.groupby('Ano')['valor'].sum().reset_index()

    plt.figure(figsize=(14, 6))

    plt.subplot(1, 2, 1)
    plt.plot(df_filtrado['data'], df_filtrado['valor'], color='red', linewidth=1.5)
    plt.title('Evolução do IPCA Mensal (Últimos 10 Anos)')
    plt.xlabel('Data')
    plt.ylabel('Variação % Mensal')
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.bar(df_agrupado_ano['Ano'], df_agrupado_ano['valor'], color='purple', edgecolor='black')
    plt.title('Inflação Acumulada por Ano')
    plt.xlabel('Ano')
    plt.ylabel('Variação % Anualizada')
    plt.grid(axis='y')

    plt.tight_layout()
    plt.show()

else:
    print("ERRO:", response.status_code)