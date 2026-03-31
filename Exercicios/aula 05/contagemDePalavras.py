import re
from collections import Counter

with open("p-escritas.txt", "r", encoding="utf-8") as f:
    texto = f.read().lower()

palavras = re.findall(r'\b\w+\b', texto)

frequencia = Counter(palavras)

top10 = frequencia.most_common(10)

for palavra, contagem in top10:
    print(palavra, contagem)