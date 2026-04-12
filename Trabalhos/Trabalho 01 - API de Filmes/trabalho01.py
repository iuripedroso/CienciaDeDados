import requests
import json

BASE_URL = "https://www.omdbapi.com/"
API_KEY = "4ae5ae73"

input_titulo = input("Digite o título do filme/série: ")

parametros = {
    "apikey": API_KEY,
    "t": input_titulo  
}

response = requests.get(BASE_URL, params=parametros)

if response.status_code == 200:
    data = response.json()

    if data.get("Response") == "False":
        print(f"ERRO: {data.get('Error', 'Título não encontrado.')}")
    else:
        print("Título encontrado.")

        # Baixa o poster
        poster_url = data.get("Poster")
        nome_imagem = None

        if poster_url and poster_url != "N/A":
            nome_imagem = f"{data['imdbID']}.jpg"
            resposta_imagem = requests.get(poster_url)
            if resposta_imagem.status_code == 200:
                with open(nome_imagem, "wb") as f_imagem:
                    f_imagem.write(resposta_imagem.content)
                print(f"Poster salvo como {nome_imagem}")

        informacoes_filtradas = {
            "imdbID":    data["imdbID"],
            "title":     data["Title"],
            "year":      data["Year"],
            "rated":     data.get("Rated"),
            "genre":     data.get("Genre"),
            "director":  data.get("Director"),
            "actors":    data.get("Actors"),
            "plot":      data.get("Plot"),
            "imdbRating": data.get("imdbRating"),
            "boxOffice": data.get("BoxOffice"),
            "type":      data.get("Type"),
            "poster_local": nome_imagem
        }

        # Carrega o JSON existente
        try:
            with open("data.json", "r", encoding="utf-8") as json_file:
                existing_data = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        # Verifica duplicata
        ja_existe = any(item["imdbID"] == informacoes_filtradas["imdbID"] for item in existing_data)

        if not ja_existe:
            existing_data.append(informacoes_filtradas)
            with open("data.json", "w", encoding="utf-8") as json_file:
                json.dump(existing_data, json_file, indent=4, ensure_ascii=False)
            print(f"'{data['Title']}' foi adicionado com sucesso!")
        else:
            print(f"'{data['Title']}' já está no arquivo. Nenhuma duplicata criada.")

else:
    print("ERRO HTTP:", response.status_code)