#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Bauyrzhan Ospan"
__copyright__ = "Copyright 2019, Buyqaw LLP"
__version__ = "1.0.1"
__maintainer__ = "Bauyrzhan Ospan"
__email__ = "bospan@cleverest.tech"
__status__ = "Development"

import asyncio
import logging
from datetime import datetime
from pymongo import MongoClient
import json


# Logging setup
FORMAT = '%(asctime)-15s: %(message)s'
logging.basicConfig(format=FORMAT, level='INFO')
logger = logging.getLogger('tcpserver')

# Database setup
client = MongoClient('mongodb://database:27017/')
db = client.vend

# Dict of writers
writers = {}


def lograw(addr, data):
    item_doc = {
        'data': data,
        'IP': addr,
        'date': datetime.now()
    }
    db.rawlog.insert_one(item_doc)


def opened(name, typer, addr):
    item_doc = {
        'vid': name,
        'IP': addr,
        'date': datetime.now(),
        'type': typer
    }
    db.door.insert_one(item_doc)


def cashin(name, amount, addr):
    item_doc = {
        'vid': name,
        'IP': addr,
        'date': datetime.now(),
        'amount': amount
    }
    db.cash.insert_one(item_doc)


async def analyze(data, name, addr):
    print(data)
    if name == "boss":
        try:
            who = data.split("-")[0]
            what = data.split("-")[1]
            try:
                toclient = writers[who]
                toclient.write(what.decode())
                await toclient.drain()
            except:
                raise Exception("there is no client: " + str(who))
        except:
            raise Exception("boss doesn`t know commands")
    data = data.strip("\n")
    if data == "i" or data == "o":
        opened(name, data, addr)
    elif data.isnumeric():
        cashin(name, data, addr)
    else:
        raise Exception("command is not in type")


async def handle_echo(reader, writer):
    name = None
    try:
        while True:
            data = await reader.read(100)
            if data:
                lograw(str(writer.get_extra_info('peername')), data.decode())
            if data and len(data.decode().split(";")) == 2:
                message = data.decode()
                ip = writer.get_extra_info('peername')[0]
                logger.info("IP is: " + str(ip))
                if not name:
                    name = message.split(";")[0]
                    logger.info("Name of %s is %s", str(ip), name)
                    writers[name] = writer
                command = message.split(";")[1]
                logger.info("Message is: %s from %s", str(command.strip("\n")), str(ip))
                if name == "boss":
                    try:
                        who = data.split("-")[0]
                        what = data.split("-")[1]
                        try:
                            toclient = writers[who]
                            toclient.write(what.decode())
                            await toclient.drain()
                        except:
                            raise Exception("there is no client: " + str(who))
                    except:
                        raise Exception("boss doesn`t know commands")
                data = command.strip("\n")
                logger.info("Data is: " + str(data))
                if data == "i" or data == "o":
                    opened(name, data, ip)
                elif data.isnumeric():
                    cashin(name, data, ip)
                else:
                    raise Exception("command is not in type")
                writer.write(b"1\n")
                await writer.drain()
            else:
                logger.warning('Protocol problem: %s from %s', 'disconnected', str(writer.get_extra_info('peername')))
                writer.close()
                break
    except Exception as e:
        d = {'clientip': writer.get_extra_info("peername")[0], 'user': "somestuff"}
        logger.warning('Protocol problem: %s from %s', e, str(writer.get_extra_info('peername')))
        writer.close()


def main():
    loop = asyncio.get_event_loop()
    coro = asyncio.start_server(handle_echo, '0.0.0.0', 7777, loop=loop)
    server = loop.run_until_complete(coro)
    # Serve requests until Ctrl+C is pressed
    logger.info('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()


if __name__=="__main__":
    main()

