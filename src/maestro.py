#!/usr/bin/python3.8
import os, sys, json, string
from scraper import Scrapper
HELP = \
"""`Maestro` is a program that collects news information from the `Agencia
lupa` and` g1` websites related to fake news about COVID-19. To run the program
(only in UNIX environments):

python maestro.py [arg]

arg: output directory
"""

class Maestro:
    def __init__(self, output_folder:str, db_config:str=False):
        self.out_folder = output_folder


    def get_data(self):
        covid_news = list(filter(self.covidometer, Scrapper.scrap()))
        self.__save_data(covid_news)


    def __save_data(self, data):
        name = "covid-news"
        with open(self.out_folder+'/'+ name + '.json', 'w') as f2:
            data = json.dumps(data, indent="    ", ensure_ascii=False)
            print(data)
            f2.writelines(data)


    def covidometer(self, news):
        covid_descriptors = {'covid, covid-19', 'covid19', 'coronavírus', 
        'coronavirus', 'corona', 'vírus', 'virus', 'oms', 'cloroquina', 'vacina',
        'pandemia', 'emergencial', 'epidemia', 'hidroxicloroquina', 'saúde', 'saude',
        'quarentena', 'mascara', 'máscara', 'respirador', 'respiradores'}

        text = news['title']+ " " +news['description']
        text = set(self.sanitize(text).split(' '))
        return len(text.intersection(covid_descriptors)) >= 1


    def sanitize(self, text:str) -> str:
        table = str.maketrans('', '', string.punctuation+'‘’')
        text = text.strip().lower().translate(table)
        return text



        
if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("At least one positional argument needed.\n\t-h, --help: For help")
        sys.exit(1)


    if sys.argv[1].lower() == '-h' or sys.argv[1].lower() == '--help':
        print(HELP)
        sys.exit(1)
    else:
        if not os.path.isdir(sys.argv[1]):
            print("Invalid directory path")
            sys.exit(1)

    out_folder = sys.argv[1]

    maestro = Maestro(out_folder)
    maestro.get_data()

