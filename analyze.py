#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import logging
import random
from tqdm import tqdm
import datetime
from pymongo import MongoClient
from pprint import pprint
from flask import Markup


# Logging setup
FORMAT = '%(asctime)-15s: %(message)s'
logging.basicConfig(format=FORMAT, level='INFO')
logger = logging.getLogger('tcpserver')


# Database setup
client = MongoClient('mongodb://localhost:27017/')
db = client.vend


def data(val):
    sumit = 0
    els = 0
    for el in val:
        sumit = sumit + int(el["amount"])
        els = els + 1
    if els>0:
        ave = sumit/els
    else:
        ave = 0
    return [sumit, ave, els]


def history(start, end, vid):
    json = {'$and': [{'date':{'$gte':start, '$lt': end}}, {'vid': str(vid)}]}
    result = db.cash.find(json)
    return result


def Average(lst): 
    return sum(lst) / len(lst) 


def head_charts(BID="All"):
    if BID == "All":
        thisweek = datetime.datetime.now().isocalendar()[1]-1
        year = datetime.datetime.now().isocalendar()[0]
        start = datetime.datetime.strptime(str(str(year) + \
            "-" + str(thisweek) + "-1"), "%Y-%W-%w")
        end = datetime.datetime.strptime(str(str(year) + \
            "-" + str(thisweek) + "-0"), "%Y-%W-%w")

        start_last = datetime.datetime.strptime(str(str(year) + \
            "-" + str(thisweek-1) + "-1"), "%Y-%W-%w")
        end_last = datetime.datetime.strptime(str(str(year) + \
            "-" + str(thisweek-1) + "-0"), "%Y-%W-%w")
        datess = [start, end]
        vids = db.cash.distinct("vid")
        bids = db.bid.distinct("bid")
        bidvids = db.vid.find()
        output = []
        sums = 0
        sums_last = 0
        clients = 0
        mins = []
        for vid in vids:
            sums += int(data(history(start, end, vid))[0])
            sums_last += int(data(history(start_last, end_last, vid))[0])
            clients += int(data(history(start, end, vid))[2])
            mins.append(int(data(history(start, end, vid))[2]))
        
        
        average = Markup(str(int(sums/clients)))
        
        sumit = Markup(str(int((sums*100)/sums_last)))
        yesterday = Markup(str(int(sums_last)))
        clients = Markup(clients)
        sums = Markup(str(int(sums/100)))

        min_clients = Markup(min(mins))
        max_clients = Markup(max(mins))
        ave_clients = Markup(Average(mins))


    else:
        thisweek = datetime.datetime.now().isocalendar()[1]-1
        year = datetime.datetime.now().isocalendar()[0]
        start = datetime.datetime.strptime(str(str(year) + \
            "-" + str(thisweek) + "-1"), "%Y-%W-%w")
        end = datetime.datetime.strptime(str(str(year) + \
            "-" + str(thisweek) + "-0"), "%Y-%W-%w")

        start_last = datetime.datetime.strptime(str(str(year) + \
            "-" + str(thisweek-1) + "-1"), "%Y-%W-%w")
        end_last = datetime.datetime.strptime(str(str(year) + \
            "-" + str(thisweek-1) + "-0"), "%Y-%W-%w")
        datess = [start, end]
        vids = db.cash.distinct("vid")
        bids = db.bid.distinct("bid")
        bidvids = db.vid.find()
        output = []
        sums = 0
        sums_last = 0
        clients = 0
        mins = []
        for vid in vids:
            if db.vid.find({"vid": vid})["bid"] == BID:
                sums += int(data(history(start, end, vid))[0])
                sums_last += int(data(history(start_last, end_last, vid))[0])
                clients += int(data(history(start, end, vid))[2])
                mins.append(int(data(history(start, end, vid))[2]))
        
        average = Markup(str(int(sums/clients)))
        
        sumit = Markup(str(int((sums*100)/sums_last)))
        yesterday = Markup(str(int(sums_last)))
        clients = Markup(clients)
        sums = Markup(str(int(sums/100)))

        min_clients = Markup(min(mins))
        max_clients = Markup(max(mins))
        ave_clients = Markup(Average(mins))

    return sumit, sums, average, clients, min_clients, max_clients, ave_clients

print(head_charts())