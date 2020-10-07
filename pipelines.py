# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import  logging
import pymongo
class MongoDBPipeline(object):
    collection_name ="Imdb Movies"

    def open_spider(self, spider):
        self.client = pymongo.MongoClient("mongodb+srv://Baba_yaga:Python4ever@cluster0.b8bu6.mongodb.net/<dbname>?retryWrites=true&w=majority")
        self.db = self.client["IMDB"]
        logging.warning("Spider Opened from Pipeline")

    def close_spider(self, spider):
            self.client.close()
            logging.warning("Spideer close from Pipeline")

    def process_item(self, item, spider):
        self.db[self.collection_name].insert(item)
        return item
