import mysql.connector
import json

# Carrega o JSON
with open('config.json') as f:
    config = json.load(f)

try:
    cnx = mysql.connector.connect(
        user=config['user'],
        password=config['password'],
        host=config['host'],
        database=config['database']
    )
    
    print("Conectou com sucesso!")
    cnx.close()

except mysql.connector.Error as err:
    print("Erro:", err)