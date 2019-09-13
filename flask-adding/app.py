#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Bauyrzhan Ospan"
__copyright__ = "Copyright 2019, Buyqaw LLP"
__version__ = "1.0.1"
__maintainer__ = "Bauyrzhan Ospan"
__email__ = "bospan@cleverest.tech"
__status__ = "Development"

# standard imports for flask server
from gevent import monkey

monkey.patch_all()

import requests
import glob
import os
from flask import Flask, render_template, session, request, json, jsonify, url_for, Markup, redirect
import random
import re
from pprint import pprint
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import random
from flask import Markup
import copy
from werkzeug.utils import secure_filename
import base64

# standard import of os
import os

# import socket programming library
import socket

# import python-mongo library
from pymongo import MongoClient

# import thread module
import threading

# import module to parse json
import json

# import datetime to deal with timestamps
import datetime
import logging

# global variables

# client = MongoClient('mongodb://database:27017/')
# db = client.buyqaw

async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)

# Logging setup
FORMAT = '%(asctime)-15s: %(message)s'
logging.basicConfig(format=FORMAT, level='INFO')
logger = logging.getLogger('tcpserver')


# Database setup
client = MongoClient('mongodb://database:27017/')
db = client.vend


# analytics functions

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


def sales(BID="All"):
    if BID == "All":
        thisweek = datetime.datetime.now().isocalendar()[1]-1
        year = datetime.datetime.now().isocalendar()[0]
        datess = []
        for el in range(10):
            start = datetime.datetime.strptime(str(str(year) + \
                "-" + str(thisweek-el) + "-1"), "%Y-%W-%w")
            end = datetime.datetime.strptime(str(str(year) + \
                "-" + str(thisweek-el) + "-0"), "%Y-%W-%w")
            datess.append([start, end])
        vids = db.cash.distinct("vid")
        bids = db.bid.distinct("bid")
        bidvids = db.vid.find()
        output = []
        for vid in vids:
            sums = []
            aveg = []
            for date in datess:
                datelabel = date[0].isocalendar()[1]
                sums.append({"val":data(history(date[0], date[1], vid))[0], "date":datelabel})
                aveg.append({"val":data(history(date[0], date[1], vid))[1], "date":datelabel})
            output.append({"sum": sums, "ave": aveg, "vid": vid, \
                "bid": int(db.vid.find_one({"vid": vid})["bid"])})
        byVIDS = output
        dates = output[0]["sum"]
        byBIDS = {}
        allbyBIDS = {"sum": [], 'aveg': []}
        coefall = 0
        for date in dates:
            allbyBIDS['sum'].append({'date': date['date'], 'val': 0})
            allbyBIDS['aveg'].append({'date': date['date'], 'val': 0})
        for bid in bids:
            byBIDS[bid] = {"sum": [], 'aveg': []}
            for date in dates:
                byBIDS[bid]['sum'].append({'date': date['date'], 'val': 0})
                byBIDS[bid]['aveg'].append({'date': date['date'], 'val': 0})
            for out in byVIDS:
                if out["bid"] == bid:
                    for el in range(len(out['sum'])):
                        byBIDS[bid]['sum'][el]['val'] += out['sum'][el]['val']
                        byBIDS[bid]['aveg'][el]['val'] += out['ave'][el]['val']

            coef = int(db.bid.find_one({"bid": bid})["number_of_places"])
            for i in range(len(byBIDS[bid]["aveg"])):
                byBIDS[bid]["aveg"][i]['val'] = byBIDS[bid]["aveg"][i]['val']/coef
                allbyBIDS['aveg'][i]['val'] += byBIDS[bid]["aveg"][i]['val']
                allbyBIDS['sum'][i]['val'] += byBIDS[bid]["sum"][i]['val']
        coefall = len(byBIDS)
        for i in range(len(allbyBIDS["aveg"])):
                allbyBIDS["aveg"][i]['val'] = allbyBIDS["aveg"][i]['val']/coefall    


        allSUM = []
        for i in range(len(allbyBIDS["sum"])):
            value = {'date': allbyBIDS['sum'][i]['date']}
            value['All'] = allbyBIDS['sum'][i]['val']
            for el in byBIDS.keys():
                value[str(el)] = byBIDS[el]['sum'][i]['val']
            allSUM.append(value)
        
        for i in range(len(allSUM)):
            datet = str(str(year) + \
                "-" + str(allSUM[i]["date"]) + "-0")
            allSUM[i]["date"] = int(datetime.datetime.strptime(datet, "%Y-%W-%w").strftime("%s%f"))/1000
            
            allbyBIDS["aveg"][i]["date"] = int(datetime.datetime.strptime(datet, "%Y-%W-%w").strftime("%s%f"))/1000
        

        sales_graphic = "data: " + str(allSUM)

        xkey = "'date'"
        keys = list(allSUM[0].keys())
        ykeys = list(set(keys)-set(['date']))

        names = db.bid.find()
        labels = ykeys.copy()

        for el in names:
            for n, i in enumerate(labels):
                if i == "All":
                    labels[n] = "Все"
                elif str(i) == str(el['bid']):
                    labels[n] = str(el['name']['ru'])

        lineColors = []
        for i in range(len(labels)): 
            lineColors.append("#%06x" % random.randint(0, 0xFFFFFF))

        
        sales_graphic += ", xkey: " + xkey + ", ykeys: " + str(ykeys) + ', labels: ' + \
            str(labels) + ", lineColors: " + str(lineColors)

        avg_graphic = "data: " + str(allbyBIDS["aveg"]) + ", \
            xkey: 'date', ykeys: ['val'], labels: ['Средний']"

        charts_pie = "colors: " + str(lineColors) + ", data: "

        chart = []
        for el in byBIDS.keys():
            names = db.bid.find()
            name2 = ""
            for mem in names:
                if str(mem["bid"]) == str(el):
                    name2 = mem["name"]["ru"]
            chart.append({"label": name2, "value": byBIDS[el]["sum"][0]["val"]})
        
        charts_pie += str(chart)

        return [charts_pie, sales_graphic, avg_graphic]

    else:
        thisweek = datetime.datetime.now().isocalendar()[1]-1
        year = datetime.datetime.now().isocalendar()[0]
        datess = []
        for el in range(10):
            start = datetime.datetime.strptime(str(str(year) + \
                "-" + str(thisweek-el) + "-1"), "%Y-%W-%w")
            end = datetime.datetime.strptime(str(str(year) + \
                "-" + str(thisweek-el) + "-0"), "%Y-%W-%w")
            datess.append([start, end])
        vids = db.cash.distinct("vid")
        bids = db.bid.distinct("bid")
        bidvids = db.vid.find()
        output = []
        for vid in vids:
            sums = []
            aveg = []
            for date in datess:
                datelabel = date[0].isocalendar()[1]
                sums.append({"val":data(history(date[0], date[1], vid))[0], "date":datelabel})
                aveg.append({"val":data(history(date[0], date[1], vid))[1], "date":datelabel})
            output.append({"sum": sums, "ave": aveg, "vid": vid, \
                "bid": int(db.vid.find_one({"vid": vid})["bid"])})
        byVIDS = output
        sums = []
        aveg = []
        for date in byVIDS[0]['sum']:
            sums.append({'date': date['date']})
            aveg.append({'date': date['date'], "average": 0})
        
        coef = 0
        for el in byVIDS:
            if str(el["bid"]) == str(BID):
                coef += 1
                for date in el['sum']:
                    for i in range(len(sums)):
                        if sums[i]["date"] == date["date"]:
                            sums[i][el["vid"]] = date["val"]
                for date2 in el['ave']:
                    for i in range(len(sums)):
                        if aveg[i]["date"] == date2["date"]:
                            aveg[i]['average'] += date2["val"]

        for i in range(len(aveg)):
            aveg[i]['average'] = aveg[i]['average']/coef
        
        for i in range(len(sums)):
            datet = str(str(year) + \
                "-" + str(sums[i]["date"]) + "-0")
            sums[i]["date"] = int(datetime.datetime.strptime(datet, "%Y-%W-%w").strftime("%s%f"))/1000
            
            aveg[i]["date"] = int(datetime.datetime.strptime(datet, "%Y-%W-%w").strftime("%s%f"))/1000
        
        sales_graphic = "data: " + str(sums)
        xkey = 'date'
        keys = list(sums[0].keys())
        ykeys = list(set(keys)-set(['date']))
        labels = ykeys
        lineColors = []
        for i in range(len(labels)): 
            lineColors.append("#%06x" % random.randint(0, 0xFFFFFF))
        
        sales_graphic += ", xkey: '" + xkey + "', ykeys: " + str(ykeys) + ', labels: ' + \
            str(labels) + ", lineColors: " + str(lineColors)
        
        dates = output[0]["sum"]
        byBIDS = {}

        for bid in bids:
            byBIDS[bid] = {"sum": [], 'aveg': []}
            for date in dates:
                byBIDS[bid]['sum'].append({'date': date['date'], 'val': 0})
                byBIDS[bid]['aveg'].append({'date': date['date'], 'val': 0})
            for out in byVIDS:
                if out["bid"] == bid:
                    for el in range(len(out['sum'])):
                        byBIDS[bid]['sum'][el]['val'] += out['sum'][el]['val']
                        byBIDS[bid]['aveg'][el]['val'] += out['ave'][el]['val']

            coef2 = int(db.bid.find_one({"bid": bid})["number_of_places"])
            for i in range(len(byBIDS[bid]["aveg"])):
                byBIDS[bid]["aveg"][i]['val'] = byBIDS[bid]["aveg"][i]['val']/coef2
        
        avg_graphic = "data: " + str(byBIDS[int(BID)]["aveg"]) + ", \
            xkey: 'date', ykeys: ['val'], labels: ['Средний']"


        charts_pie = "colors: " + str(lineColors) + ", data: "

        chart = []
        for el in byVIDS:
            if str(el["bid"]) == str(BID):
                chart.append({"label": el["vid"], "value": el["sum"][0]["val"]})
        
        charts_pie += str(chart)


        return [charts_pie, sales_graphic, avg_graphic]


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
        min_clients = Markup(int((min(mins)/int(clients))*100))
        max_clients = Markup(int((max(mins)/int(clients))*100))
        ave_clients = Markup(int((Average(mins)/int(clients))*100))
        sums = Markup(str(int(sums/100)))
        clients = Markup(clients)
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
        for vida in vids:
            if db.vid.find_one({"vid": vida})["bid"] == BID:
                sums += int(data(history(start, end, vida))[0])
                sums_last += int(data(history(start_last, end_last, vida))[0])
                clients += int(data(history(start, end, vida))[2])
                mins.append(int(data(history(start, end, vida))[2]))
        
        average = Markup(str(int(sums/clients)))
        sumit = Markup(str(int((sums*100)/sums_last)))
        yesterday = Markup(str(int(sums_last)))
        min_clients = Markup(int((min(mins)/int(clients))*100))
        max_clients = Markup(int((max(mins)/int(clients))*100))
        ave_clients = Markup(int((Average(mins)/int(clients))*100))
        sums = Markup(str(int(sums/100)))
        clients = Markup(clients)
    return sumit, sums, average, clients, min_clients, max_clients, ave_clients



def gen_table(BID="All"):
    base = '<tr><td>{vid}</td><td>{buildname}</td><td name="timey">{date}</td>\
            <td><span class="badge bg-red">{amount}</span></td></tr>'
    if BID == "All":
        vids = db.cash.distinct("vid")
        bids = db.bid.distinct("bid")
        bidvids = db.vid.find()
        last_opens = []
        for vid in vids:
            d = db.door.find_one({"vid": vid}).copy()
            v = db.vid.find_one({"vid": vid}).copy()
            name = db.bid.find_one({"bid": int(v["bid"])})["name"]["ru"]
            start = d["date"]
            end = datetime.datetime.utcnow()
            summa = '{:20,}'.format(float(data(history(start, end, vid))[0]))
            last_opens.append({"sum": summa, "time": str(int(datetime.datetime.timestamp(start))), \
                "vid": vid, "name": name})
        
        msg = ""
        for el in last_opens:
            new = base
            msg = msg + new.replace("{vid}", str(el["vid"])).replace("{buildname}", el["name"])\
                .replace("{date}", str(el["time"])).replace("{amount}", str(el["sum"]))
        return msg


# index page
@app.route('/', methods=['POST', 'GET'])  # Вывод на экраны
def glavnaia():
    charts_pie, sales_graphic, avg_graphic = sales()
    charts_pie = Markup(charts_pie)
    sales_graphic = Markup(sales_graphic)
    avg_graphic = Markup(avg_graphic)

    head = '<li><a href="/place/{vid}"><i class="fa fa-circle-o"></i>{name}</a></li>'

    head2 = ""
    names = list(db.bid.find()).copy()
    new = []

    for el in names:
        main = head
        head2 = head2 + main.replace("{vid}", str(el["bid"])).replace("{name}", el["name"]["ru"])

    head = Markup(head2)
    name_of_data = "Все данные"

    sumit, sums, average, clients, min_clients, max_clients, ave_clients = head_charts()
    table_gen = Markup(gen_table())
    return render_template('index.html', **locals())


@app.route('/place/<BID>', methods=['POST', 'GET'])  # Вывод на экраны
def place(BID):
    charts_pie, sales_graphic, avg_graphic = sales(BID)
    charts_pie = Markup(charts_pie)
    sales_graphic = Markup(sales_graphic)
    avg_graphic = Markup(avg_graphic)

    head = '<li><a href="/place/{vid}"><i class="fa fa-circle-o"></i>{name}</a></li>'

    head2 = ""
    names = list(db.bid.find()).copy()
    new = []

    for el in names:
        main = head
        head2 = head2 + main.replace("{vid}", str(el["bid"])).replace("{name}", el["name"]["ru"])

    head = Markup(head2)

    name_of_data = db.bid.find_one({"bid": int(BID)})["name"]["ru"]

    sumit, sums, average, clients, min_clients, max_clients, ave_clients = head_charts(BID)
    table_gen = Markup(gen_table())
    return render_template('index.html', **locals())


if __name__ == '__main__':
    # gen_table()
    socketio.run(app, host='0.0.0.0', port=80, debug=True)
