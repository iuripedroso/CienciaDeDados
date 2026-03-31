import requests

topico = "coca cola"

url = "https://api.github.com/search/repositories"
params = {
    "q": topico,
    "per_page": 5
}

response = requests.get(url, params=params)
dados = response.json()

repos = dados["items"]

for repo in repos:
    print(repo["name"], "-", repo["html_url"])