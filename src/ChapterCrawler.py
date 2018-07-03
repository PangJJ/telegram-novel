import pprint
import requests
from bs4 import BeautifulSoup

class ChapterCrawler():
	def __init__(self):
		pass
	def crawl_web(self, web_url):
		response = requests.get(web_url)
		response_data = response.text

		soup = BeautifulSoup(response_data, "html.parser")
		content = soup.findAll("div", {"class": "fr-view"})

		paragraphs = content[0].find_all('p')

		paragraphs = map(lambda para:
					para.string.replace("<p>", "").replace("</p>",""),
					filter(lambda x:x.string, paragraphs)
				)
		
		chapters = content[0].find_all("a", {"class":"chapter-nav"})
		chapter_links = [link.get('href') for link in chapters]
		
		return (paragraphs, chapter_links)



def main():
	TEST_URL = "https://www.wuxiaworld.com/novel/wu-dong-qian-kun/wdqk-chapter-40"
	ccrawler = ChapterCrawler()
	paras, neighbour_chapters = ccrawler.crawl_web(TEST_URL)


if __name__ == "__main__":
    main()
