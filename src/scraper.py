#!/usr/bin/python3.8

import os, sys, requests, json, re, datetime, logging
from bs4 import BeautifulSoup

class Scrapper:
    """
    class who holds all methods for scraping websites intended to collect
    data against fake-news       
    """

    HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
                "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                 }

    LOG_FILE = "./log/covid-scraper-" + datetime.datetime.now() .strftime("%d-%m-%y-%H:%M:%S") + ".log"
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    logging.basicConfig(filename=LOG_FILE, filemode='w', level=logging.DEBUG)


    @classmethod
    def scrap(cls) -> list:
        """input: (nothing)
        output: list of dictionaries that map basic news attributes to their content.
        The attributes are:
        title, description, imageURL, newsURL, date, time, author, source
        """ 

        logging.info("Starting Lupa scraping-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
        lupa_content = cls.scrap_lupa()

        logging.info("Starting g1 scraping-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
        g1_content = cls.scrap_g1()

        return g1_content + lupa_content


    @classmethod 
    def scrap_lupa(cls) -> dict:
        url = "https://piaui.folha.uol.com.br/lupa/"
        contents = requests.get(url, headers=cls.HEADERS).text

        # only for debug purposes
        #  open("./test.html", 'w').writelines(contents)
        #  contents = open("./test.html").read()

        soup = BeautifulSoup(contents, features='lxml')
        contents = []
        s = soup.find("div", {'class' : 'lista-noticias'})

        for child in s.findChildren('div'):
            img_url, title, description, news_url = (None, None, None, None)

            if child.has_attr("class") and (child['class'][0] == "inner" or
                                            child['class'][0] == 'bloco-meta' or
                                            child['class'][0] == 'internaPGN'):
                continue

            try:
                date_str, time_str = list(map(str.strip, child.find('div').find('div').text.split("|")))[:-1]
                date_str = date_str.replace('.', '/').strip()
                date = datetime.datetime.strptime(date_str, "%d/%m/%Y")

                if date >= datetime.datetime.now() - datetime.timedelta(days=1) :                                                                                                                  #verifica se a publicação tem mais de um dia
                    title = child.find('div').find('h2').find('a')['title'].strip()
                    description = child.find('div').find('h3').find('a').contents[0].strip()
                    img_url = child.find('a')['style'][23:-2].strip()
                    news_url = child.find('div').find('h3').find('a')['href'].strip()
                    author = child.find('div').find('h4').text.strip()                  
         
                    c = Scrapper.build_dict(title, description, img_url, news_url, date_str, time_str, date, author , 'lupa')

                    contents.append(c)
            except Exception as e:
                Scrapper.build_log(e, "Agência Lupa")

        return contents


    @classmethod 
    def scrap_g1(cls) -> list:
        url = 'https://falkor-cda.bastian.globo.com/tenants/g1/instances/__token__/posts/page/__page__'

        def get_token():                                                                                                                                                                                # capturando o token da página e colocando na url da API
            url_token = 'https://g1.globo.com/fato-ou-fake/'
            page = requests.get( url_token , headers = cls.HEADERS ).text
            pre_token = re.findall( r'/instances/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' , page )
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
            for item in js['items']:
                date_time = datetime.datetime.strptime ( item[ 'publication' ] , "%Y-%m-%dT%H:%M:%S.%fZ")
                if date_time >= datetime.datetime.now() - datetime.timedelta(days=1) :                                                                                                                  #verifica se a publicação tem mais de um dia
                    title = item["content"]['title']
                    description = item["content"]['summary']
                    img_url = item["content"]['image']['sizes']['L']['url']
                    news_url = item["content"]['url']
                    date_str = date_time.strftime("%d/%m/%Y")
                    time_str = date_time.strftime("%Hh%M")
                    date = datetime.datetime.strptime(date_str, "%d/%m/%Y")
                    author = ''

                    c = Scrapper.build_dict(title, description, img_url, news_url, date_str, time_str, date, author , 'g1')
                    contents.append(c)
                else:
                    if cont_publicacao <= 0: return contents                                                                                                                                            #isso contorna o erro da primeira pagina 
                    else: cont_publicacao -= 1
        return contents


    @staticmethod
    def build_log(e:Exception, w:str):
        logging.error(f"Something went wrong wgile running {w} function:\n\t{e}")


    @staticmethod
    def build_dict(title, description, img_url, news_url, date_str, time_str, date, author, source):
        return {'title'         : title,
                'description'   : description,
                'imageURL'      : img_url,
                'newsURL'       : news_url,
                'dateStr'       : date_str,
                'timeStr'       : time_str,
                'date'          : date,
                'author'        : author,
                'source'        : source}



# Debug driver
if __name__ == "__main__":
    print(json.dumps(Scrapper.scrap(), indent="    ", ensure_ascii=False))
