#!/usr/bin/python3.8

import os, sys
from selenium import webdriver
from bs4 import BeautifulSoup
import requests 
import json


class Data:
    def __init__(self, name, url, content):
        self.name = name
        self.url  = url
        self.content = content

class News:
    def __init__(self, img_url, title, call, news_url):
        self.img_url = img_url
        self.title = title
        self.call = call
        self.news_url = news_url

    def __str__(self):
        return f"Title: {self.title}\n"
        #  return f"Title: {self.title}\nChamada: {self.call}\nUrl notícia: {self.news_url}\nUrl imagem: {self.img_url}"


class Scrapper:
    HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                 }

    LOG_FILE = "./errors.log"
    
    @classmethod
    def scrap(cls) -> str:
        news = []

        lupa_content = cls.scrap_lupa()
        return lupa_content

    @classmethod 
    def scrap_lupa(cls) -> dict:
        url = "https://piaui.folha.uol.com.br/lupa/"
        contents = requests.get(url, headers=cls.HEADERS).text

        # only for debug purposes
        #  contents = open("./testes/test.html").read()

        soup = BeautifulSoup(contents, features='lxml')
        contents = []
        s = soup.find("div", {'class' : 'internaPGN'})

        for child in s.findChildren('div'):
            img_url, title, call, news_url = (None, None, None, None)

            if child.has_attr("class") and (child['class'][0] == "inner" or child['class'][0] == 'bloco-meta'):
                continue


            try:
                title = child.find('div').find('h2').find('a')['title'].strip()
                call = child.find('div').find('h3').find('a').contents[0].strip()
                img_url = child.find('a')['style'][23:-2].strip()
                news_url = child.find('div').find('h3').find('a')['href'].strip()
                date,time = list(map(str.strip, child.find('div').find('div').text.split("|")))[:-1]
                date = date.replace('.', '/').strip()
                author = child.find('div').find('h4').text.strip()
                
                c = Scrapper.build_dict(title, call, img_url, news_url, date, time, author)

                contents.append(c)
            except Exception as e:
                #TODO: using an dedicated method for logging
                print("------------------------------------------------------")
                print(e)
                print(child)
                print("------------------------------------------------------\n\n\n\n")

        
        return contents
    
    @staticmethod
    def build_log():
        #TODO
        pass

    @staticmethod
    def build_dict(title, call, img_url, news_url, date, time, author):
        return {'title'   : title,
                'call'    : call,
                'img_url' : img_url,
                'news_url': news_url,
                'date'    : date,
                'time'    : time,
                'author'  : author}


    @classmethod 
    def scrap_g1(cls):
        url = ""

        #TODO: Theo
        pass


if __name__ == "__main__":
    print(json.dumps(Scrapper.scrap(), indent="    ", ensure_ascii=False))
