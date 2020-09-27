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

        logging.info("Starting bbc scraping-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
        bbc_content = cls.scrap_bbc()

        logging.info("Starting sanarmed scraping-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
        sanarmed_content = cls.scrap_sanarmed()

        return g1_content + lupa_content + bbc_content + sanarmed_content


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
        
                if date >= datetime.datetime.now() - datetime.timedelta(days=3) :                                                                                                                  #verifica se a publicação tem mais de um dia
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

            try:
                for item in js['items']:
                    date_time = datetime.datetime.strptime ( item[ 'publication' ] , "%Y-%m-%dT%H:%M:%S.%fZ")
                    if date_time >= datetime.datetime.now() - datetime.timedelta(days=3) :                                                                                                                  #verifica se a publicação tem mais de um dia
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
            except: 
                pass
        return contents

    @classmethod
    def scrap_sanarmed(cls) -> dict:
        url = 'https://www.sanarmed.com/coronavirus/fake-news'
        contents = requests.get(url, headers=cls.HEADERS).text
        soup = BeautifulSoup(contents, features='lxml')
        contents = []
        contents1 = []
        i = 0

        s = soup.find("div", {'class': 'styles__WrapperFeed-sc-1utrrzb-7'})
        for child in s.findChildren('div', {'class': 'styles__WrapperTopo-sc-1utrrzb-5'}):
            try:
                date = child.find("span",{"type" : "Sub100"}).text.strip() + '/' \
                       + child.find("span",{"type" : "p100"}).text.strip()
                date_time = datetime.datetime.strptime(date, "%m/%d/%Y")
                if date_time >= datetime.datetime.now() - datetime.timedelta(days=3):
                    date_str = date_time.strftime("%d/%m/%Y")
                    time_str = date_time.strftime("%Hh%M")
                    #time_str = '-'
                    date = datetime.datetime.strptime(date_str, "%d/%m/%Y")
                    l = []
                    l.insert(0, date_str)
                    l.insert(1, time_str)
                    l.insert(2, date)
                    contents1.append(l)
            except Exception as e:
                Scrapper.build_log(e, "Sanarmed")
        for child in s.findChildren('a', {'rel': 'noopener noreferrer'}):
            try:
                if contents1[i][2] >= datetime.datetime.now() - datetime.timedelta(days=3):
                    title = child.find(class_='item-title').text.strip()
                    description = child.find(class_='item-abstract').text.strip()
                    img_url = child.find(class_='styles__ImgNews-sc-17s39zh-9 qlGGe')['src'].strip()
                    news_url = child['href'].strip()
                    author = '-'
                    c = Scrapper.build_dict(title, description, img_url, news_url, contents1[i][0], contents1[i][1], contents1[i][2],
                                   author, 'Sanarmed')
                    contents.append(c)
                    i += 1
                    if (i > (len(contents1) - 1)):
                        break
            except Exception as e:
                Scrapper.build_log(e, "Sanarmed")
        return contents

    @classmethod
    def scrap_bbc(cls) -> dict:

        url = 'https://www.bbc.com/portuguese/topics/c95y354381pt'
        contents = requests.get(url, headers=cls.HEADERS).text
        soup = BeautifulSoup(contents, features='lxml')
        contents = []

        s = soup.find("ol", {'class': 'gs-u-m0 gs-u-p0 lx-stream__feed qa-stream'})

        for child in s.findChildren('li', {'class': 'lx-stream__post-container placeholder-animation-finished'}):  # class é importante pois há outros li sem relação
            img_url, title, description, news_url = (None, None, None, None)
            try:

                date1 = child.find(class_='qa-post-auto-meta').text.strip()
                date2 = Scrapper.monthInNumber(date1)
                date2 = date2.replace(' ', '/').replace('/', ' ', 1)
                date_time = datetime.datetime.strptime(date2, "%H:%M %d/%m/%Y")
                if date_time >= datetime.datetime.now() - datetime.timedelta(days=3):
                    title = child.find(class_='lx-stream-post__header-text gs-u-align-middle').text.strip()
                    description = child.find(class_='lx-stream-related-story--summary qa-story-summary').text.strip()
                    img_url = child.find(class_='qa-srcset-image lx-stream-related-story--index-image qa-story-image')[
                        'src'].strip()
                    news_url = 'https://bbc.com' + child.find(class_='qa-heading-link lx-stream-post__header-link')[
                        'href'].strip()
                    date_str = date_time.strftime("%d/%m/%Y")
                    time_str = date_time.strftime("%Hh%M")
                    date = datetime.datetime.strptime(date_str, "%d/%m/%Y")
                    try:
                        author = child.find(
                            class_='qa-contributor-name lx-stream-post__contributor-name gel-long-primer gs-u-m0').text.strip()
                    except:
                        author = '-' #algumas notícias não possuem autor
                    c = Scrapper.build_dict(title, description, img_url, news_url, date_str, time_str, date, author, 'BBC')
                    contents.append(c)
            except Exception as e:
                Scrapper.build_log(e, "BBC")
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

    @staticmethod
    def monthInNumber(datas):
        datas = datas.split(' ')
        if (datas[2].lower() == 'janeiro'):
            datas[2] = '01'
        elif (datas[2].lower() == 'fevereiro'):
            datas[2] = '02'
        elif (datas[2].lower() == 'março'):
            datas[2] = '03'
        elif (datas[2].lower() == 'abril'):
            datas[2] = '04'
        elif (datas[2].lower() == 'maio'):
            datas[2] = '05'
        elif (datas[2].lower() == 'junho'):
            datas[2] = '06'
        elif (datas[2].lower() == 'julho'):
            datas[2] = '07'
        elif (datas[2].lower() == 'agosto'):
            datas[2] = '08'
        elif (datas[2].lower() == 'setembro'):
            datas[2] = '09'
        elif (datas[2].lower() == 'outubro'):
            datas[2] = '10'
        elif (datas[2].lower() == 'novembro'):
            datas[2] = '11'
        elif (datas[2].lower() == 'dezembro'):
            datas[2] = '12'
        x = ''
        for y in datas:
            x = x + ' ' + y
        return x.strip()
        

# Debug driver
if __name__ == "__main__":
    print(json.dumps(Scrapper.scrap(), indent="    ", ensure_ascii=False))
