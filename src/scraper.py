#!/usr/bin/python3.8

import os, sys
from bs4 import BeautifulSoup
import requests 
import json
import re
import datetime


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
        g1_content = cls.scrap_g1()
    
        return g1_content + lupa_content

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
                
                c = Scrapper.build_dict(title, call, img_url, news_url, date, time, author , 'lupa')

                contents.append(c)
            except Exception as e:
                #TODO: using an dedicated method for logging
                print("------------------------------------------------------")
                print(e)
                print(child)
                print("------------------------------------------------------\n\n\n\n")

        
        return contents

    @classmethod 
    #TODO try como vai ser feito
    def scrap_g1(cls) -> list:
        url = 'https://falkor-cda.bastian.globo.com/tenants/g1/instances/__token__/posts/page/__page__'

        def get_token():                                                                                                                                                                                # capturando o token da página e colocando na url da API
            url_token = 'https://g1.globo.com/fato-ou-fake/'
            page = requests.get( url_token , headers = cls.HEADERS ).text
            pre_token = re.findall ( r'/instances/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' , page )
            return pre_token[ 0 ].strip('/instances/')
        
        def get_json( url_base , i ):
            url = url_base.replace( '__page__' , str( i ) ) 
            response_json = requests.get( url , headers = cls.HEADERS ).text 
            return json.loads( response_json )

        url = url.replace( '__token__' , get_token() )    

        cont_publicacao = 1                                                                                                                                                                             #variavel usada para pular a primeira publicação, parece que api tem problemas
        contents = list()
        for i in range( 1 , 6 ):                                                                                                                                                                        #percorre até as últimas 5 páginas, isso para caso falhar coletar somente até as últimas 50 manchetes
            js = get_json( url , i )
            for item in js[ 'items']:
                date_time = datetime.datetime.strptime ( item[ 'publication' ] , "%Y-%m-%dT%H:%M:%S.%fZ")
                if date_time >= datetime.datetime.now() - datetime.timedelta(days=1) :                                                                                                                  #verifica se a publicação tem mais de um dia
                    title = item[ "content"][ 'title' ]
                    call = item[ "content"][ 'summary' ]
                    img_url = item[ "content"][ 'image']['url']
                    news_url = item[ "content"][ 'url' ]
                    date = date_time.strftime("%d/%m/%Y")
                    time = date_time.strftime("%Hh%M")
                    author = ''
                    
                    c = Scrapper.build_dict(title, call, img_url, news_url, date, time, author , 'g1')
                    contents.append(c)
                else:
                    if cont_publicacao <= 0: return contents                                                                                                                                            #isso contorna o erro da primeira pagina 
                    else: cont_publicacao -= 1
        return contents

    @staticmethod
    def build_log():
        #TODO
        pass

    @staticmethod
    def build_dict(title, call, img_url, news_url, date, time, author , source):
        return {'title'   : title,
                'call'    : call,
                'img_url' : img_url,
                'news_url': news_url,
                'date'    : date,
                'time'    : time,
                'author'  : author,
                'source'  : source}



if __name__ == "__main__":
    print(json.dumps(Scrapper.scrap(), indent="    ", ensure_ascii=False))
