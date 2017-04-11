# -*- coding: utf-8 -*-

import pymongo
import traceback


class MyMongo(object):
    def __init__(self, host='127.0.0.1', port=27017):
        self.client = None
        self.db = None
        try:
            self.client = pymongo.MongoClient(host=host, port=port)
        except:
            traceback.print_exc()
            self.client = None

    def get_db(self, db_name):
        if self.client:
            try:
                self.db = self.client[db_name]
            except:
                traceback.print_exc()

    def insert_doc(self, db_name, doc_name, doc_list):
        # data_dic - {data:[doc1, doc2...docN]}
        self.get_db(db_name)  # get database to self.db
        if self.db is None:
            return False
        try:
            doc = self.db[doc_name]
            doc.insert(doc_list)
        except:
            traceback.print_exc()
            return False
        return True
