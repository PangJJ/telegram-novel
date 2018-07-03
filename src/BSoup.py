from bs4 import BeautifulSoup
import requests
import sys

test_url = "https://www.wuxiaworld.com/novel/wu-dong-qian-kun"

r = requests.get(test_url)
data = r.text

soup = BeautifulSoup(data, "html.parser")
filtered_links = []
filter_text = "wdqk-chapter"

for link in soup.find_all('a'):
  chapter_link = link.get('href')
  if filter_text in chapter_link:
    filtered_links.append(chapter_link)

import pprint
pprint.pprint(filtered_links)
  

