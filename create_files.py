#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import logging
import random
from tqdm import tqdm
import datetime

# Logging setup
FORMAT = '%(asctime)-15s: %(message)s'
logging.basicConfig(format=FORMAT, level='INFO')
logger = logging.getLogger('tcpserver')


bids = [
    {
        "bid": 1,
        "name": {
            "ru": "Аэропорт",
            "kz": "Ауежай",
            "qz": "Auezhai",
            "eng": "Airport"
        },
        "number_of_places": 2
    },
    {
        "bid": 2,
        "name": {
            "ru": "Поликлиника",
            "kz": "Аурухана",
            "qz": "Auruhana",
            "eng": "Medical center"
        },
        "number_of_places": 1
    }
]

vids = [
    {
        "vid": "1235",
        "bid": "1"
    },
    {
        "vid": "1234",
        "bid": "1"
    },
    {
        "vid": "2345",
        "bid": "2"
    }
]

vidss = [
    "2345",
    "1235",
    "1234"
]


def random_date():
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days = 90)
    """Generate a random datetime between `start` and `end`"""
    return start + datetime.timedelta(
        # Get a random amount of seconds between `start` and `end`
        seconds=random.randint(0, int((end - start).total_seconds())),
    )


from pymongo import MongoClient

# Database setup
client = MongoClient('mongodb://database:27017/')
db = client.vend

def insertVID(doc):
    db.vid.insert_one(doc)

def insertBID(doc):
    db.bid.insert_one(doc)

for bid in bids:
    insertBID(bid)
    logger.info("Inserted BID: " + str(bid["bid"]))

for vid in vids:
    insertVID(vid)
    logger.info("Inserted VID: " + str(vid["vid"]))


def cashin(number):
    for num in tqdm(range(number)):
        item_doc = {
            'vid': random.choice(vidss),
            'IP': "192.168.1.1",
            'date': random_date(),
            'amount': random.choice(["200", "500", "1000", "400", "600"])
        }
        db.cash.insert_one(item_doc)


def opening(number):
    vids = db.cash.distinct("vid")
    for num in tqdm(range(number)):
        for vid in vids:
            date1 = random_date()
            item_doc = {
                'vid': vid,
                'IP': "192.168.1.1",
                'date': date1,
                'type': "o"
            }
            item_doc2 = {
                'vid': vid,
                'IP': "192.168.1.1",
                'date': date1 + datetime.timedelta(seconds = 10),
                'type': "c"
            }
            db.door.insert_one(item_doc)
            db.door.insert_one(item_doc2)


cashin(500)
opening(4)
