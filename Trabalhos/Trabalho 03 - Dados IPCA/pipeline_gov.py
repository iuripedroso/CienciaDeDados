import requests
import pandas as pd
import mysql.connector
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import logging
import json
from datetime import datetime, timedelta

logging.basicConfig(
    filename='pipeline_gov.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def executar_pipeline():
    try:
        hoje = datetime.now()
        data_final = hoje.strftime('%d/%m/%Y')
        data_inicial = (hoje - timedelta(days=3650)).strftime('%d/%m/%Y')
        
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados?formato=json&dataInicial={data_inicial}&dataFinal={data_final}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        df = pd.DataFrame(response.json())
        df['data'] = pd.to_datetime(df['data'], format='%d/%m/%Y')
        df['valor'] = pd.to_numeric(df['valor'])
        
        df_filtrado = df.copy()


        with open('config.json', 'r') as file:
            configuracoes_db = json.load(file)

        try:
            cnx = mysql.connector.connect(**configuracoes_db)
        except mysql.connector.Error as err:
            logging.error(f"Erro ao conectar no banco: {err}")
            print(f"Erro crítico ao conectar: {err}")
            return 
        
        is_ativo = cnx.is_connected() if callable(getattr(cnx, 'is_connected', None)) else cnx.is_connected
        if is_ativo:
            logging.info(f"Conexão ativa no banco: {cnx.database}")
        
        cursor = cnx.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dolar_historico (
                data_referencia DATE PRIMARY KEY,
                valor_venda DECIMAL(10,4)
            )
        """)
        
        query_insert = """
            INSERT INTO dolar_historico (data_referencia, valor_venda)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE valor_venda = VALUES(valor_venda)
        """
        
        registros = [
            (row['data'].strftime('%Y-%m-%d'), row['valor']) 
            for _, row in df_filtrado.iterrows()
        ]
        
        if not cnx.in_transaction:
            cursor.executemany(query_insert, registros)
            cnx.commit()
            logging.info(f"Processamento de {cursor.rowcount} linhas diárias concluído.")

        cursor.execute('SELECT data_referencia, valor_venda FROM dolar_historico ORDER BY data_referencia ASC')
        
        dados_db = []
        for valor in cursor:
            dados_db.append(valor)
            
        df_db = pd.DataFrame(dados_db, columns=['Data', 'Valor'])
        df_db['Data'] = pd.to_datetime(df_db['Data'])
        df_db['Valor'] = pd.to_numeric(df_db['Valor'])
        
        media = df_db['Valor'].mean()
        maximo = df_db['Valor'].max()
        minimo = df_db['Valor'].min()
        
        print(f"Estatísticas Dólar (10 anos) -> Média: R$ {media:.2f} | Máximo: R$ {maximo:.2f} | Mínimo: R$ {minimo:.2f}")
        
        fig = plt.figure(figsize=(16, 10))
        
        # --- Gráfico 1: Linha ---
        plt.subplot(2, 2, 1)
        plt.plot(df_db['Data'], df_db['Valor'], color='green', linewidth=1)
        plt.title('Evolução Diária do Dólar (Venda)')
        plt.xlabel('Ano')
        plt.ylabel('Preço (R$)')
        plt.grid(True)
        legenda_linha = mpatches.Patch(color='green', label='Valor de venda do dólar (R$)')
        plt.legend(handles=[legenda_linha], loc='upper left', fontsize=9)

        # --- Gráfico 2: Boxplot ---
        plt.subplot(2, 2, 2)
        bp = plt.boxplot(df_db['Valor'], vert=False, patch_artist=True,
                         boxprops=dict(facecolor='steelblue', color='steelblue'),
                         medianprops=dict(color='darkorange', linewidth=2),
                         whiskerprops=dict(color='steelblue'),
                         capprops=dict(color='steelblue'),
                         flierprops=dict(marker='o', color='steelblue', alpha=0.5))
        plt.title('Dispersão e Outliers do Valor do Dólar')
        plt.xlabel('Valor (R$)')
        caixa = mpatches.Patch(facecolor='steelblue', edgecolor='steelblue', label='Intervalo interquartil (IQR)')
        mediana = mpatches.Patch(facecolor='darkorange', edgecolor='darkorange', label='Mediana')
        bigodes = mpatches.Patch(facecolor='white', edgecolor='steelblue', label='Bigodes (mín/máx sem outliers)')
        plt.legend(handles=[caixa, mediana, bigodes], loc='upper right', fontsize=8)

        # --- Gráfico 3: Pizza ---
        plt.subplot(2, 1, 2)
        df_db['Faixa'] = pd.cut(df_db['Valor'], bins=5)
        distribuicao = df_db['Faixa'].value_counts().sort_index()
        cores = plt.cm.Paired.colors[:len(distribuicao)]
        wedges, texts, autotexts = plt.pie(
            distribuicao,
            labels=None,
            autopct='%1.1f%%',
            startangle=140,
            colors=cores
        )
        plt.legend(
            wedges,
            [str(faixa) for faixa in distribuicao.index],
            title='Faixas de Preço (R$)',
            loc='upper left',
            bbox_to_anchor=(1, 1),
            fontsize=9
        )
        plt.title('Porcentagem de Tempo por Faixa de Preço (Últimos 10 Anos)')
        
        plt.tight_layout()
        plt.savefig('graficos_dolar_trabalho3.png', bbox_inches='tight')
        print("Gráficos atualizados salvos na pasta atual!")
        
        cursor.close()
        demonstrar_comandos_internos(cnx)
        cnx.disconnect() 
        
    except Exception as e:
        logging.error(f"Falha no pipeline: {str(e)}")
        print(f"Erro crítico: {str(e)}")

def demonstrar_comandos_internos(cnx):
    try:
        if hasattr(cnx, 'get_database'):
            cnx.get_database()
            
        cnx.cmd_init_db('teste')
        cnx.set_database('teste')
        cnx.cmd_query("SELECT 1")
        cnx.cmd_quit()
    except Exception as err:
        logging.warning(f"Comandos internos do slide testados: {err}")

if __name__ == "__main__":
    executar_pipeline()