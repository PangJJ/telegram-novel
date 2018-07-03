import json
import requests
import time
import urllib
import pprint

from TelegramWrapper import TelegramAPIWrapper as Telegram
from Bot import Bots

from ChapterScraper import GlossaryCrawler
from ChapterCrawler import ChapterCrawler


class TelegramHandler():

    def __init__(self, bot_name):
        self.bot_info = Bots().bot_details[bot_name]
        self.bot_token = self.bot_info["TOKEN"]
        self.bot_username = self.bot_info["USERNAME"]
        self.telegram = Telegram(self.bot_token)
        self.col_width=49

        # state tracking
        self.glossary_url = "https://www.wuxiaworld.com/novel"
        self.chapter_title = "wu-dong-qian-kun"
        self.filter_text = "-chapter-"
        self.last_update_id = None

    def get_url(self, url):
        response = requests.get(url)
        content = response.content.decode("utf-8")
        return content
  
    def get_json_from_url(self, url):
        content = self.get_url(url)
        json_data = json.loads(content)
        return json_data

    def get_updates(self, offset=None):
        url = self.telegram.get_updates_url(offset)
        json_data = self.get_json_from_url(url)
        pprint.pprint(json_data)
        return json_data

    def get_last_chat_id_and_text(self, updates):
        num_updates = len(updates["result"])

        # updates["result"][-1] to get the last update
        last_update = updates["result"][-1]["message"]
        text = last_update["text"]
        chat_id = last_update["chat"]["id"]
    
        return (chat_id, text)

    def send_message(self, chat_id, text):
        # print(text)
        text = urllib.parse.quote_plus(text)
        url = self.telegram.send_message_url(chat_id, text)
        self.get_url(url)

    def get_last_update_id(self, updates):
        return max([int(update["update_id"]) for update in updates["result"] ])

    def paginate_message(self, messages):
        combined_msg = [""]

        for idx,message in enumerate(messages):
            if len(combined_msg[-1]) + len(message) < 4095:
                combined_msg[-1] = "\n".join([combined_msg[-1], message])
            else:
                combined_msg.append(message)
        return combined_msg

    def options_parser(self, json_data):
        try:
            data = json_data["message"]
        except KeyError:
            data = json_data["message"]
        return (data["text"], data["chat"]["id"])

    def change_chapter_name(self, selector, chat_id):
        self.chapter_title = selector.split(" ")[1]

        glossary_crawler = GlossaryCrawler(self.glossary_url, 
                                self.chapter_title, self.filter_text)
        chapters = glossary_crawler.crawl_chapter()
        glossary_crawler.persist_chapters(chapters)

        return

    def default_selector_router(self, selector, chat_id):
        router = {
            "/start": (self.send_message, (chat_id, "Welcome")),
            "/crawl": (self.change_chapter_name, (selector,chat_id))
        }

        try:
            return router[selector[:6]]
        except KeyError:
            glossary_crawler = GlossaryCrawler(self.glossary_url, 
                                           self.chapter_title, 
                                           self.filter_text)
            return (glossary_crawler.get_chapter_url, (selector,))

    def send_chapter(self, update):
        
        selector, chat_id = self.options_parser(update)
        route_fn, arguments = self.default_selector_router(selector, chat_id)
        chapter_url = route_fn(*arguments)

        if chapter_url is None or len(chapter_url) == 0:
            return

        #tests for chapter if selector is not a known command
        #chapter_url = glossary_crawler.get_chapter_url(selector)
        ccrawler = ChapterCrawler()

        try:
            chapter_url = chapter_url[0][0]
        except:
            self.send_message(chat_id, "unknown command")
            return

        paras, neighbours_chapters = ccrawler.crawl_web(chapter_url)
        paras = self.paginate_message(paras)

        #Header
        self.send_message(chat_id,"Chapter: " + chapter_url)
        self.send_message(chat_id,'-'*self.col_width)

        for para in paras:
            try:
                self.send_message(chat_id, para)
            except Exception as e:
                print(e)
                
        #Footer
        self.send_message(chat_id,'-'*self.col_width)
        for n in neighbours_chapters:
            self.send_message(chat_id,n)
        self.send_message(chat_id,"="*self.col_width)
        print("Completed chapter: {}".format(selector))

    
def main():
    
    telegram_handler = TelegramHandler("novel-reader-stg")

    while True:
        updates = telegram_handler.get_updates(telegram_handler.last_update_id)
        
        if len(updates["result"]) > 0:
            telegram_handler.last_update_id = telegram_handler.get_last_update_id(updates) + 1
        for update in updates["result"]:
            telegram_handler.send_chapter(update)

if __name__ == "__main__":
    main()
