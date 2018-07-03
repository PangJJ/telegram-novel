import pprint
import sys
import sqlite3
import requests
from bs4 import BeautifulSoup

class GlossaryCrawler():
    
    def __init__(self, glossary_url, chapter_title, 
                filter_text=None, db_name="data/novel-db"):
        
        self.glossary_url = glossary_url if glossary_url.startswith("https")\
                          else "https://{glossary_url}".format(
                              glossary_url=glossary_url)
        self.chapter_title = chapter_title.lower()
        self.chapter_title_min = self.chapter_title.replace("-","")
        self.filter_text = self.chapter_title + "-chapter" if not filter_text\
                           else filter_text

        # init db upon creation
        self.db_name = db_name
        self.db = sqlite3.connect(self.db_name)
        self.cursor = self.db.cursor()

    def close_conn(self):
        try:
            self.db.close()
        except Exception as e:
            print(e)

    def __del__(self):
        self.close_conn()
    def __exit__(self):
        self.close_conn()

    def open_conn(self):
        self.db = sqlite3.connect(self.db_name)
        self.cursor = db.cursor()

    def commit_close_conn(self):
        self.db.commit()
        self.db.close()

    def commit(self):
        self.db.commit()


    def crawl_chapter(self):
        response = requests.get("{}/{}".format(self.glossary_url,self.chapter_title))
        response_data = response.text
        
        # Parses site
        soup = BeautifulSoup(response_data, "html.parser")
        chapter_suffix = {}
    
        # find all links, and filter them
        chapter_suffix = {
                chapter_link
                    for chapter_link in filter(
                        lambda chapter_link: self.filter_text in chapter_link,
                        [link.get('href') for link in soup.find_all('a')]
                    )
        }

        # Need to sort, as sometimes chapters repeat themselves
        chapter_suffix = list(chapter_suffix)
        chapter_suffix.sort()
        return chapter_suffix 

  
    def persist_chapters(self, chapters):
        self.cursor.execute(
        """
          CREATE TABLE IF NOT EXISTS {table}(
            id INTEGER PRIMARY KEY AUTOINCREMENT, base_url TEXT, 
            chapter_url TEXT, full_url TEXT)
        """.format(table=self.chapter_title_min)
        )
        self.commit()
    
        for idx, chapter in enumerate(chapters):
            chapter = chapter.split('/')[-1]
            full_url = "{}/{}/{}".format(self.glossary_url,self.chapter_title,chapter)
            self.cursor.execute(
                """
                INSERT INTO {table}(base_url, chapter_url, full_url)
                    VALUES(:base_url,:chapter_url,:full_url)
                """.format(table=self.chapter_title_min),
                {"base_url":self.glossary_url,"chapter_url":chapter,"full_url":full_url}
            )
        self.commit()

    def get_chapter_url(self, chapter_selector):
        self.cursor.execute("""
            SELECT full_url 
            FROM {table}
            WHERE chapter_url = :chapter_url
        """.format(table=self.chapter_title_min),
        {"chapter_url":chapter_selector})
        rows = self.cursor.fetchall()
        return rows

    def query_all(self):
        self.cursor.execute("""SELECT * FROM {}""".format(self.chapter_title_min))
        rows = self.cursor.fetchall()

        return rows

    def clean_all(self):
        self.cursor.execute("""DELETE FROM {}""".format(self.chapter_title_min))
        self.commit()


def main():
    glossary_url = "https://www.wuxiaworld.com/novel"
    chapter_title = "wu-dong-qian-kun"
    filter_text = "wdqk-chapter"
    # chapter_title = "coiling-dragon"
    # filter_text = "cd-book"

    glossary_crawler = GlossaryCrawler(glossary_url, chapter_title, filter_text)
    # glossary_crawler.clean_all()
    # chapters = glossary_crawler.crawl_chapter()
    # glossary_crawler.persist_chapters(chapters)
    # query_data = glossary_crawler.query_all()
    # query_data = glossary_crawler.get_chapter_url("wdqk-chapter-999")
    query_data = glossary_crawler.get_chapter_url("random_string")
    # for data in query_data:
        # print(data)

if __name__ == "__main__":
    main()
