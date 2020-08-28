from pymongo import MongoClient
import logging
import os, urllib

class PickleDB(MongoClient):
    name = "PickleDB"
    def __init__(self):
        self.logger = logging.getLogger(self.name or self.__class__.__name__)
        formatter = logging.Formatter("[%(asctime)s %(levelname)s] (%(name)s: %(filename)s:%(lineno)d) > %(message)s")

        handler = logging.StreamHandler()
        handler.setLevel('DEBUG')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.setLevel('DEBUG')
    
    def connect(self):
        DB_FULL = os.getenv("DB_FULL")
        if not DB_FULL:
            DB_FULL = "mongodb://%s:%s@%s:%s/%s?authSource=admin" % (
                os.getenv("DB_ID"),
                urllib.parse.quote(os.getenv("DB_PW")),
                os.getenv("DB_HOST"),
                os.getenv("DB_PORT"),
                os.getenv("DB_DB")
            )

        super().__init__(DB_FULL)
        
        try:
            self.server_info()
            self.logger.info("Connected")
        except:
            self.logger.error("ERROR in connecting")