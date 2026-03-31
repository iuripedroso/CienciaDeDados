import requests
from bs4 import BeautifulSoup

url = "https://www.python.org"

response = requests.get(url)
html = response.text

soup = BeautifulSoup(html, "html.parser")

titulos = soup.find_all("h2")

for t in titulos:
    print(t.get_text(strip=True))