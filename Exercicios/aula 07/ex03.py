import requests
import pandas as pd

# API pública (não precisa de chave)
url = "https://jsonplaceholder.typicode.com/users"

response = requests.get(url)

if response.status_code == 200:
    dados = response.json()
    
    # Criando DataFrame
    df = pd.DataFrame(dados)
    
    print(df)
else:
    print(f"Erro: {response.status_code}")