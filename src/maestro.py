#!/usr/bin/python3.8
import os, sys, json
from scraper import Scrapper

class Maestro:
    def __init__(self, output_folder:str, db_config:str=False):
        self.out_folder = output_folder


    def get_data(self):
        #  for web_content in Scrapper.scrap():
        self.__save_data(Scrapper.scrap())


    def __save_data(self, data):
        name = "teste"
        with open(self.out_folder+'/'+ name, 'w') as f2:
            data = json.dumps(data, indent="    ", ensure_ascii=False)
            print(data)
            f2.writelines(data)




if __name__ == "__main__":
    out_folder = sys.argv[1]

    maestro = Maestro(out_folder)
    maestro.get_data()

























#
