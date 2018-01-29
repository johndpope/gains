#!/bin/python3

import json
import requests
import random
import base64
import string
import os
import configparser

from Crypto.Cipher import AES
from .ccxt_balance import CcxtClient
from django.conf import settings
# balance, cancelorder, limitorder, openorders, orderbook, json, ticker, tradefees, tradehistory,

exchanges = ['ALL', 'BINANCE', 'GDAX', 'KRAKEN', 'POLONIEX', 'BITFINEX', 'VAULTORO', 'TRUEFX', 'QUADRIGACX', 'LUNO', 'GEMINI', 'YOBIT', 'LIVECOIN', 'VIRCUREX',  'GATECOIN', 'THEROCK', 'RIPPLE', 'QUOINE', 'TAURUS',  'MERCADOBITCOIN', 'OKCOIN', 'POLONIEX', 'PAYMIUM', 'HITBTC', 'LAKEBTC', 'INDEPENDENTRESERVE', 'ITBIT', 'GDAX', 'KRAKEN', 'EMPOEX', 'DSX', 'CRYPTONIT', 'CRYPTOPIA', 'CRYPTOFACILITIES', 'COINMATE', 'COINFLOOR', 'COINBASE',  'CEXIO', 'CCEX', 'CAMPBX',  'BTCTRADE', 'BTCMARKETS',  'BTCC',  'BLOCKCHAIN', 'BLEUTRADE', 'BITTREX', 'BITSTAMP', 'BITSO', 'BITMARKET', 'BITFINEX', 'BITCUREX', 'BITCOINIUM', 'BITCOINDE', 'BITCOINCORE', 'BITCOINCHARTS', 'BITCOINAVERAGE', 'BITBAY', 'ANX']
# exchanges = ['GDAX', 'KRAKEN', 'POLONIEX', 'BITFINEX']
default_limit_ask = {"order_type":"ASK","order_specs":{"base_currency":"ETH","quote_currency":"BTC","volume":"0.1","price":"10000","test":True}}
default_limit_bid = {"order_type":"BID","order_specs":{"base_currency":"ETH","quote_currency":"BTC","volume":"0.01","price":"0.0001","test": True}}

def send( data, method, config, json=False):
    if json:
        r = requests.get(config.get('xi_url') + "/" + method, json=data).text
    else:
        r = requests.get(config.get('xi_url') + "/" + method, params=data).text
    return r

def decrypt(payload):
    config = getConfig(settings)
    payload = json.loads(payload)
    plain_text = ""
    #    try:
    init_vector = payload['iv']
    encrypted_data = payload['encrypted_data']
    init_vector = base64.b64decode(init_vector)
    encrypted_data = base64.b64decode(encrypted_data)
    encryption_suite = AES.new(config['aes_key'], AES.MODE_CFB, init_vector)

    plain_text = encryption_suite.decrypt(encrypted_data).decode('utf-8')
    #plain_text = plain_text.decode('utf-8')
    #except:
    #    plain_text = json.dumps(payload)

    return plain_text

def encrypt( data, config):
    #https://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
    init_vector = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(16))

    #encryption_suite = AES.new(key, AES.MODE_CFB, init_vector, segment_size=128)
    encryption_suite = AES.new(config['aes_key'], AES.MODE_CFB, init_vector)
    json_data = json.dumps(data)

    # encrypt returns an encrypted byte string
    cipher_text = encryption_suite.encrypt(json_data)

    # encrypted byte string is base 64 encoded for message passing
    base64_cipher_byte_string = base64.b64encode(cipher_text)

    # base 64 byte string is decoded to utf-8 encoded string for json serialization
    base64_cipher_string = base64_cipher_byte_string.decode('utf-8')

    encrypted_request = {"iv": init_vector,
            "encrypted_data": base64_cipher_string}
    return encrypted_request

def getCreds(exchange, config):

    try:
        creds = {
                "exchange": exchange.lower(),
                "key": config.api_key,
                "secret": config.secret
                }
    except:
        raise ValueError('exchange ' + exchange.lower() + ' does not have credentials')

    return creds

def getConfig(settings):
    cfg = { "xi_url": settings.XI_URL,
            "aes_key": settings.AES_KEY
            }
    return cfg

def requestExchange(exchange, method, encrypted=True):
    config = getConfig(settings)
    response = {}
    if exchange.lower() == 'all':
        for an_exchange in exchanges:
            data = {"exchange": an_exchange.lower()}
            r = send(data, method, config)
            data = decrypt(r)
            response.update({exchange.upper(): data})
    else:
        data = {"exchange": exchange.lower()}
        data = send(data, method, config)

        if encrypted == True:
            data = decrypt(data)

        response.update({exchange.upper(): data})
    return response

def directRequest( method, data=None):
    response = {}
    config = getConfig(settings)
    r = send(data, method, config, True)
    data = decrypt(r)
    response.update({method: data})
    return response

def request( method, data=None):
    config = getConfig(settings)
    response = {}
    if data['exchange'].lower() == 'all':
        for an_exchange in exchanges:
            data.update({"exchange": an_exchange.lower()})
            r = send(data, method, config)
            data = decrypt(r)
            response.update({an_exchange.upper(): data})
    else:
        r = send(data, method, config)
        data = decrypt(r)
        response.update({data['exchange'].upper(): data})
    return response

def requestOrderBook(method, exchange, base, quote):
    config = getConfig(settings)
    response = {}
    if exchange.lower() == 'all':
        for an_exchange in exchanges:
            data = {'exchange':an_exchange,'base_currency':base,'quote_currency':quote}
            r = send(encrypt(data, config), method, config)
            data = decrypt(r)
            response.update({an_exchange.upper(): data})
    else:
        data = {'exchange':exchange,'base_currency':base,'quote_currency':quote}
        r = send(encrypt(data, config), method, config)
        data = decrypt(r)
        response.update({exchange.upper(): data})
    return response


def requestLimitOrder(exchange, limitorder, ordertype):
    order = ""
    if ordertype.lower() == 'ask':
        order = 'ask'
    elif ordertype.lower() == 'bid':
        order = 'bid'
    else:
        order = ""

    if order == "":
        print("Must set order type to ASK or BID");
    else:
        config = getConfig(settings)
        response = {}
        #if exchange.lower() == 'all':
        #    for exchange in exchanges:
        #        creds = getCreds(exchange, config)
        #        limitorder.update({"exchange_credentials":creds})
        #        r = send(encrypt(limitorder, config), "limitorder", config)
        #       data = decrypt(r)
        #       response.update({exchange.upper(): data})
        #else:
        r = send(encrypt(limitorder, config), "limitorder", config)
        data = decrypt(r)
        response.update({exchange.upper(): data})
    return response


def requestFillOrKill(orders):
    config = getConfig(settings)
    response = {}

    index = 0
    modified_orders = []

    while (index < len(orders)):
        if not orders[index].get('exchange_credentials'):
            exchange = orders[index]['exchange']
            creds = getCreds(exchange, config)
            orders[index].update({"exchange_credentials": creds})

        modified_orders.append(orders[index])
        index = index + 1

    r = send(encrypt(modified_orders, config), "fillorkill", config)
    data = decrypt(r)
    response.update({"fillorkill": data})
    return response


def requestInterExchangeArbitrage(orders, external_creds=None):
    config = getConfig(settings)
    response = {}

    index = 0
    modified_orders = []

    if (external_creds==None):
        while (index < len(orders)):
            exchange = orders[index]['exchange']
            creds = getCreds(exchange, config)
            orders[index]['order'].update({"exchange_credentials": creds})
            modified_orders.append(orders[index]['order'])
            index = index + 1
            r = send(encrypt(modified_orders, config), "interexchangearbitrage", config)

    r = send(encrypt(orders, config), "interexchangearbitrage", config)
    data = decrypt(r)
    response.update({"interexchangearbitrage": data})
    return response


def requestBalance(exchange):
    config = getConfig(settings)
    response = {}

    if isinstance(exchange, dict):
        exchange_name = exchange['exchange_credentials']['exchange']
        exchange = exchange['exchange_credentials']
    else:
        exchange_name = exchange

    if exchange_name.lower() == 'all':
        for exchange in exchanges:
            creds = getCreds(exchange, config)
            r = send(encrypt(creds, config), "balance", config)
            data = decrypt(r)
            response.update({exchange.upper(): data})
    else:
        # creds = getCreds(exchange, config)
        r = send(encrypt(exchange, config), "balance", config)
        data = decrypt(r)
        # response.update({exchange.upper(): data})
        response = json.loads(data)
    return response


def requestExchangeAccountBalance(exchange):

    response = {}
    ccxtclient = CcxtClient(exchange)
    status, response = ccxtclient.get_account_balance()
    # Status Show Ccxt Exchange Class Exist or not
    if not status:
        return requestBalance(exchange)
    else:
        return response


def requestOpenOrders(exchange):
    config = getConfig(settings)
    response = {}
    temp = {}
    history_req = {}
    temp.update({"page_length": "10"})
    history_req.update({"trade_params": temp})

    if isinstance(exchange, dict):
        exchange_name = exchange['exchange_credentials']['exchange']
        exchange = exchange['exchange_credentials']
    else:
        exchange_name = exchange

    if exchange_name.lower() == 'all':
        for exchange in exchanges:
            creds = getCreds(exchange, config)
            r = send(encrypt(creds, config), "openorders", config)
            data = decrypt(r)
            response.update({exchange.upper(): data})
    else:
        # creds = getCreds(exchange, config)
        r = send(encrypt(exchange, config), "openorders", config)
        data = decrypt(r)
        # response.update({exchange.upper(): data})
        response = data
    return response


def requestFundingHistory( exchange, method="fundinghistory"):
    config = getConfig(settings)
    response = {}
    temp = {}
    history_req = {}
    temp.update({"page_length": "10"});
    history_req.update({"trade_params": temp});

    if isinstance(exchange,dict):
        exchange_name = exchange['exchange_credentials']['exchange']
    else:
        exchange_name = exchange

    if exchange_name.lower() == 'all':
        for exchange in exchanges:
            creds = getCreds(exchange, config)
            history_req.update({"exchange_credentials": creds});
            r = send(encrypt(history_req, config), method, config)
            data = decrypt(r)
            response.update({exchange.upper(): data})
    else:
        #creds = getCreds(exchange, config)
        r = send(encrypt(exchange, config), method, config)
        data = decrypt(r)
        #response.update({exchange.upper(): data})
        response = data
    return response


def requestAmTradeHistroy(exchange):
    config = getConfig(settings)
    response = {}
    if not exchange.get('trade_params'):
        temp = {}
        temp.update({"page_length": "10"})
        exchange.update({"trade_params": temp})

    r = send(encrypt(exchange, config), "tradehistory", config)
    data = decrypt(r)
    return data


def requestAmFundingHistroy(exchange):
    print('calling funding history with', exchange)
    config = getConfig(settings)
    response = {}
    if not exchange.get('trade_params'):
        temp = {}
        temp.update({"page_length": "10"})
        exchange.update({"trade_params": temp})

    r = send(encrypt(exchange, config), "fundinghistory", config)
    data = decrypt(r)
    return data


def requestTradeHistory(exchange, settings, config, method="tradehistory"):
    config = getConfig(settings, config)
    response = {}
    temp = {}
    history_req = {}
    temp.update({"page_length": "10"});
    history_req.update({"trade_params": temp});
    if exchange.lower() == 'all':
        for exchange in exchanges:
            creds = getCreds(exchange, config)
            history_req.update({"exchange_credentials": creds});
            r = send(encrypt(history_req, config), method, config)
            data = decrypt(r)
            response.update({exchange.upper(): data})
    else:
        creds = getCreds(exchange, config)
        history_req.update({"exchange_credentials": creds});
        r = send(encrypt(history_req, config), method, config)
        data = decrypt(r)
        response.update({exchange.upper(): data})
    return response


def cancelLimitOrder( exchange, order_id):
    config = getConfig(settings)
    response = {}
    order_to_cancel = {}
    if exchange.lower() == 'all':
        for exchange in exchanges:
            creds = getCreds(exchange, config)
            order_to_cancel.update({"exchange_credentials": creds});
            order_to_cancel.update({"order_id": order_id});
            r = send(encrypt(order_to_cancel, config), "cancelorder", config)
            data = decrypt(r)
            response.update({exchange.upper(): data})
    else:
        creds = getCreds(exchange, config)
        order_to_cancel.update({"exchange_credentials": creds});
        order_to_cancel.update({"order_id": order_id});
        r = send(encrypt(order_to_cancel, config), "cancelorder", config)
        data = decrypt(r)
        response.update({exchange.upper(): data})
    return response


def amCancelLimitOrder(exchange_dict, order_id):
    config = getConfig(settings)
    exchange_dict.update({"order_id": order_id});
    r = send(encrypt(exchange_dict, config), "cancelorder", config)
    data = decrypt(r)
    if data == "true":
        return True;
    else:
        return json.loads(data)


def requestOrders(exchange, orders):
    creds = getCreds(exchange, config)
    data = {'exchange_credentials':creds,'order_ids':orders}
    config = getConfig(settings)
    response = {}
    r = send(encrypt(data, config), "getorders", config, False)
    data = decrypt(r);
    response.update({"getorders": data})
    return response

def requestAggregateOrderBooks(base, quote, exchanges):
    data = {'base_currency':base,'quote_currency':quote,'exchanges':exchanges}
    config = getConfig(settings)
    response = {}
    r = send(encrypt(data, config), "aggregateorderbooks", config, True)
    data = decrypt(r);
    response.update({"aggregateorderbooks": data})
    return response

def requestAvailableMarkets(coe_list):
    config = getConfig(settings)
    response = {}
    r = send(encrypt(coe_list, config), "availablemarkets", config, False)
    data = decrypt(r);
    response.update({"availablemarkets": data})
    return response
