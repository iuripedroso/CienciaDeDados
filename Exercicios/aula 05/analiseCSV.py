import csv

categoria_desejada = "Eletrônicos"
precos = []

with open("produtos.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    
    for linha in reader:
        if linha["categoria"] == categoria_desejada:
            precos.append(float(linha["preco"]))

# calcular média
if precos:
    media = sum(precos) / len(precos)
    print("Preço médio:", media)
else:
    print("Nenhum produto encontrado nessa categoria")