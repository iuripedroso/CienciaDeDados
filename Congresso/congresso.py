
from bs4 import BeautifulSoup
import requests
import re

from typing import Dict, Set 

url = "https://www.house.gov/representatives"
text = requests.get(url).text
soup = BeautifulSoup(text, 'html5lib')

all_urls = [a['href']
    for a in soup('a')
    if a.has_attr('href')]

#print(len(all_url))

regex = r'^https?://.*\.house\.gov/?$'

assert re.match(regex, "https://joel.house.gov")
assert not re.match(regex, "https://joel.house.gov/biography")

good_urls = [url for url in all_urls if re.match(regex, url)]
good_urls = list(set(good_urls))

#print(len(good_urls))

press_releases: Dict[srt, Set[str]] = {}

for house_url in good_urls:
    html = requests.get(house_url).text
    soup = BeautifulSoup(html, 'html5lib')
    pr_links = [a['href'] for a in soup('a')
                if 'press releases' in a.text.lower()]
    #print(f"{house_url}: {pr_links}")
    press_releases[house_url] = pr_links

    def paragraph_mentions(text: str, keyword: str) -> bool:
        paragraphs = [p.get_text() for p in soup('p')]

        return any(keyword.lower() in paragraphs.lower()
                   for p in paragraphs)
    
for house_url, pr_links in press_releases.items():
    for pr_link in pr_links:
        try:
            html = requests.get(pr_link, timeout=5).text

            if paragraph_mentions(html, 'data'):
                print(f"Encontrados em: {house_url}")
                break

        except requests.RequestsException:
            continue