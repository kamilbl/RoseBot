#!/usr/bin/env python
# -*- coding: utf-8 -*-
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
import numpy as np
from telegram import message, update
from telegram.parsemode import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import key
import json
import datetime
import time
import talib
import numpy as np
import telegram
import prettytable as pt
from tabulate import tabulate
import emojis
import requests

# connect Binance
client = Client(key.api_key, key.api_secret)

# DataFrame pandas
df_History = pd.DataFrame()
df_Main = pd.DataFrame()
df = pd.DataFrame(columns=['Timestamp', 'Open', 'High',
                  'Low', 'Close', 'Volume', 'Close_time'])

# Market
symbol = "SHIBUSDT"

# Interval
interval = "1m"

# Telegram
#https://www.webfx.com/tools/emoji-cheat-sheet/
bot = telegram.Bot(token=key.token)

def RoseBot():
    # Trading
    operation = "BUY"         # Start operation
    budget = 523              # USDT
    saldo = 0                 # Coins

    df_Main.loc[0, "ID_Order"] = "nan"
    df_Main.loc[0, "Status_Order"] = "nan"

    hello_msg = emojis.encode(":beginner:") + " <b>ROSEBOT_1.02</b>" + emojis.encode(":beginner:") + "\t" + emojis.encode(":watch:") + "\t" + "<i>" + str(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + "</i>")

    table = GetHelloTable(symbol, budget, saldo, operation)

    tel = Telegram_Function(chat_id=key.chat_id)
    tel.TelegramSendMsg(msg=hello_msg, parse_mode=telegram.ParseMode.HTML)
    tel.TelegramSendTable(table=table, parse_mode=telegram.ParseMode.HTML)
    tel.TelegramSendBalanceTable()
    
    while True:
        try:
            df = Candles(symbol=symbol, interval=interval)
            df_Main.loc[0, "Symbol"] = symbol
            df_Main.loc[0, "Actual_price"] = (json.loads(json.dumps(client.get_symbol_ticker(symbol=symbol))))['price']
            df_Main.loc[0, "SMA"] = df.loc[len(df)-1, "SMA14"]
            df_Main.loc[0, "RSI"] = df.loc[len(df)-1, "RSI"]
            df_Main.loc[0, "Operation"] = operation
            df_Main.loc[0, "Budget"] = budget
            df_Main.loc[0, "Saldo"] = saldo
            print(df_Main)
            if float(df_Main.loc[0, "RSI"]) > 75 and float(saldo) > 0 and str(df_Main.loc[0, "ID_Order"]) == "nan":
                # SELL
                exc = Tradding(symbol=symbol, sell_price=str(df_Main.loc[0, "Actual_price"]), buy_price=None, qty=str(df_Main.loc[0, "Saldo"]), status_order=None, id_order=None)
                r = exc.SellOrder()
                df_Main.loc[0, "ID_Order"] = r[0]
                df_Main.loc[0, "Status_Order"] = r[1]
            elif float(df_Main.loc[0, "RSI"]) < 25 and budget > 0 and str(df_Main.loc[0, "ID_Order"]) == "nan":
                # BUY
                symbol_info = client.get_symbol_info(symbol=symbol)
                stepSize = str(symbol_info['filters'][2]['stepSize']).find("1")
                x_qty = float(df_Main.loc[0, "Budget"]) / float(df_Main.loc[0, "Actual_price"])
                stepDot = str(x_qty).find(".")
                x_qty = str(x_qty)[0:stepDot+stepSize]
                exc = Tradding(symbol=symbol, sell_price=None, buy_price=str(df_Main.loc[0, "Actual_price"]), qty=str(x_qty), status_order=None, id_order=None)
                r = exc.BuyOrder()
                df_Main.loc[0, "ID_Order"] = r[0]
                df_Main.loc[0, "Status_Order"] = r[1]
            if str(df_Main.loc[0, "ID_Order"]) != "nan":
                # CHECK
                exc = Tradding(symbol=symbol, sell_price=None, buy_price=None, qty=None, status_order=None, id_order=str(df_Main.loc[0, "ID_Order"]))
                r = exc.CheckOrder()
                df_Main.loc[0, "ID_Order"] = r[0]
                df_Main.loc[0, "Status_Order"] = r[1]
                if r[2] is not None:
                    saldo = r[2]
                    budget = r[3]
                    operation = r[4]
        except NameError as e:
            print(e) 


def Candles(symbol, interval):
    client = Client(key.api_key, key.api_secret)
    try:
        req = requests.get('https://www.google.com/').status_code
        if req == 200:
            candles = client.get_klines(symbol=symbol, interval=interval, limit=200)
            opentime, lopen, lhigh, llow, lclose, lvol, closetime = [], [], [], [], [], [], []
            for candle in candles:
                candle[0] = datetime.datetime.fromtimestamp(candle[0] / 1000)
                opentime.append(candle[0])
                lopen.append(candle[1])
                lhigh.append(candle[2])
                llow.append(candle[3])
                lclose.append(candle[4])
                lvol.append(candle[5])
                candle[6] = datetime.datetime.fromtimestamp(candle[6] / 1000)
                closetime.append(candle[6])
            df['Timestamp'] = opentime
            df['Open'] = np.array(lopen).astype(np.float)
            df['Open'] = df['Open'].map('{:.8f}'.format)
            df['High'] = np.array(lhigh).astype(float)
            df['High'] = df['High'].map('{:.8f}'.format)
            df['Low'] = np.array(llow).astype(float)
            df['Low'] = df['Low'].map('{:.8f}'.format)
            df['Close'] = np.array(lclose).astype(float)
            df['Volume'] = np.array(lvol).astype(float)
            df['Close_time'] = closetime
            df['Volume'] = df['Volume'].map('{:.0f}'.format)
            df['Close1000'] = df['Close'] * 10000
            df['BBupper'], df['BBmiddle'], df['BBlower'] = talib.BBANDS(df['Close1000'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
            df['BBupper'] = df['BBupper'] / 10000
            df['BBupper'] = df['BBupper'].map('{:.8f}'.format)
            df['BBmiddle'] = df['BBmiddle'] / 10000
            df['BBmiddle'] = df['BBmiddle'].map('{:.8f}'.format)
            df['BBlower'] = df['BBlower'] / 10000
            df['BBlower'] = df['BBlower'].map('{:.8f}'.format)
            df['SMA14'] = talib.SMA(df['Close'], timeperiod=14)
            df['SMA14'] = df['SMA14'].map('{:.8f}'.format)
            df['RSI'] = talib.RSI(df['Close1000'], timeperiod=14)
            df['RSI'] = df['RSI'].map('{:.1f}'.format)
            df['SAR'] = talib.SAR(df['High'], df['Low'], 0.02, 0.2)
            df['SAR'] = df['SAR'].map('{:.8f}'.format)
            df['EMA100'] = talib.EMA(df['Close'], timeperiod=100)
            df['FAST_EMA'] = talib.EMA(df['Close'], timeperiod=64)
            df['SLOW_EMA'] = talib.EMA(df['Close'], timeperiod=128)
            df['MACD'] = df['SLOW_EMA'] - df['FAST_EMA']
            df['MACD'] = df['MACD'].map('{:.8f}'.format)
            return(df)
    except BinanceAPIException as e:
        print(e)
        time.sleep(5)
        client = Client(key.api_key, key.api_secret)
            
def GetBalances():
    dfAccount = pd.DataFrame()
    info = client.get_account()              
    dfAccount = pd.json_normalize(info['balances'])
    dfAccount = dfAccount[((dfAccount.free != "0.00000000") | (dfAccount.locked != "0.00000000")) & ((dfAccount.free != "0.00") | (dfAccount.locked != "0.00"))].reset_index(drop=True)
    
    for i in range(0, len(dfAccount)):
        if dfAccount.loc[i, "asset"] != "USDT":
            price = (json.loads(json.dumps(client.get_symbol_ticker(symbol=str(dfAccount.loc[i, "asset"]) + "USDT"))))['price']
            dfAccount.loc[i, "BalanceUSDT"] = round((float(dfAccount.loc[i, "free"]) + float(dfAccount.loc[i, "locked"])) * float(price), 2)
        else:
            dfAccount.loc[i, "BalanceUSDT"] = round(float(dfAccount.loc[i, "free"]) + float(dfAccount.loc[i, "locked"]), 2)
    dfAccount = dfAccount.sort_values(by=['BalanceUSDT'], ascending=False).reset_index(drop=True)
    return(dfAccount)

def GetHelloTable(symbol, budget, saldo, operation):
    table = pt.PrettyTable(['Option', 'Value'])
    table.align['Option'] = 'l'
    table.align['Value'] = 'r'

    data = [
        ("Symbol", symbol),
        ("Budget", budget),
        ("Saldo", saldo),
        ("Operation", operation),
    ]
    for option, value in data:
        table.add_row([option, value])
    return table

def GetBalanceTable():
    dfAccount = GetBalances()
    dfAccount = dfAccount.rename(columns = {'asset': 'Asset', 'free': 'Free', 'locked': 'Locked'}, inplace = False)
    dfAccount['Free'] = dfAccount['Free'].astype(np.float)
    dfAccount['Free'] = dfAccount['Free'].map('{:,.8f}'.format)
    dfAccount['Locked'] = dfAccount['Locked'].astype(np.float)
    dfAccount['Locked'] = dfAccount['Locked'].map('{:,.8f}'.format)
    dfAccount['BalanceUSDT'] = dfAccount['BalanceUSDT'].astype(np.float)
    TotalBalance = dfAccount['BalanceUSDT'].sum()
    #TotalBalance = TotalBalance.map('{:,.2f}'.format)
    dfAccount['BalanceUSDT'] = dfAccount['BalanceUSDT'].map('{:,.2f}'.format)
    balancetable = tabulate(dfAccount, headers='keys', tablefmt='psql', stralign="right" , numalign="right")
    
    return balancetable, TotalBalance

class Tradding():
     # init method or constructor
    def __init__(self, symbol, sell_price, buy_price, qty, status_order, id_order):
        self.symbol = symbol
        self.sell_price = sell_price
        self.buy_price = buy_price
        self.qty = qty
        self.status_order = status_order
        self.id_order = id_order
    
    def BuyOrder(self):
        OrderBuy = client.create_order(symbol=str(self.symbol),
                                    side=client.SIDE_BUY,
                                    type=client.ORDER_TYPE_LIMIT,
                                    timeInForce=client.TIME_IN_FORCE_GTC,
                                    quantity=str(self.qty),
                                    price=str(self.buy_price),
                                    recvWindow=60000)
        time.sleep(1)
        Jorder = json.loads(json.dumps(OrderBuy))
        answer = [str(Jorder['orderId']), str(Jorder['status'])]
        return answer

    def SellOrder(self):
        OrderSell = client.create_order(symbol=str(self.symbol),
                                    side=client.SIDE_SELL,
                                    type=client.ORDER_TYPE_LIMIT,
                                    timeInForce=client.TIME_IN_FORCE_GTC,
                                    quantity=str(self.qty),
                                    price=str(self.sell_price),
                                    recvWindow=60000)
        time.sleep(1)
        Jorder = json.loads(json.dumps(OrderSell))
        answer = [str(Jorder['orderId']), str(Jorder['status'])]
        return answer
    
    def CheckOrder(self):
        check = client.get_order(symbol=str(self.symbol), 
                                orderId=str(self.id_order),
                                recvWindow=60000)
        time.sleep(1)
        print(check)
        Jorder = json.loads(json.dumps(check))
        if Jorder['status'] == "FILLED":
            if Jorder['side'] == "SELL":
                sell_msg = "<b>Sold Order</b>" + "\n" \
                            + emojis.encode(":id:") + "\t" + str(self.id_order) + "\n" \
                            + emojis.encode(":gem:") + "\tSymbol:\t" + str(Jorder['symbol']) + "\n" \
                            + emojis.encode(":gem:") + "\tSellPrice:\t" + str(Jorder['price']) + "\n" \
                            + emojis.encode(":moneybag:") + "\tMoney:\t" + str(Jorder['cummulativeQuoteQty']) + "\n" \
                            + emojis.encode(":moneybag:") + "\tFee:\t" + str(round(float(Jorder['cummulativeQuoteQty']) * 0.001,8)) + "\n" \
                            + emojis.encode(":moneybag:") + "\tMoneyWithoutFee:\t" + str(round(float(Jorder['cummulativeQuoteQty']) - float(Jorder['cummulativeQuoteQty']) * 0.001, 3)) + "\n" \
                            + emojis.encode(":moneybag:") + "\tCoin:\t" + str(Jorder['executedQty'])
                exe = Telegram_Function(key.chat_id)
                exe.TelegramSendMsg(msg=sell_msg, parse_mode=telegram.ParseMode.HTML)
                exe.TelegramSendBalanceTable()
                budget = round(float(Jorder['cummulativeQuoteQty']) - float(Jorder['cummulativeQuoteQty']) * 0.001, 3)
                answer = ["nan", "nan", 0, budget, "BUY"]
            elif Jorder['side'] == "BUY":

                symbol_info = client.get_symbol_info(symbol=str(Jorder['symbol']))
                stepSize = str(symbol_info['filters'][2]['stepSize']).find("1")
                
                executedQty = float(Jorder['executedQty'])
                stepDot = str(executedQty).find(".")
                executedQty = str(executedQty)[0:stepDot+stepSize]
                
                fee = float(executedQty) * 0.001
                stepDot = str(fee).find(".")
                fee = str(fee)[0:stepDot+stepSize]

                saldo = float(executedQty) - float(fee)
                stepDot = str(saldo).find(".")
                saldo = str(saldo)[0:stepDot+stepSize]

                buy_msg = "<b>Bought Order</b>" + "\n" \
                            + emojis.encode(":id:") + "\t" + str(self.id_order) + "\n" \
                            + emojis.encode(":gem:") + "\tSymbol:\t" + str(Jorder['symbol']) + "\n" \
                            + emojis.encode(":gem:") + "\tBuyPrice:\t" + str(Jorder['price']) + "\n" \
                            + emojis.encode(":moneybag:") + "\tCoin:\t" + str(executedQty) + "\n" \
                            + emojis.encode(":moneybag:") + "\tFee:\t" + str(fee) + "\n" \
                            + emojis.encode(":moneybag:") + "\tCoinWithoutFee:\t" + str(saldo) + "\n" \
                            + emojis.encode(":moneybag:") + "\tMoney:\t" + str(Jorder['cummulativeQuoteQty'])

                exe = Telegram_Function(key.chat_id)
                exe.TelegramSendMsg(msg=buy_msg, parse_mode=telegram.ParseMode.HTML)
                exe.TelegramSendBalanceTable()
                answer = ["nan", "nan", saldo, 0, "SELL"]
        else:
            answer = [str(Jorder['orderId']), str(Jorder['status']), "nan", "nan", str(Jorder['side'])]
            # answer[0]  # ID_ORDER      [0]
            # answer[1]  # STATUS ORDER  [1]
            # answer[2]  # SALDO         [2]
            # answer[3]  # BUDGET        [3]
            # answer[4]  # SIDE          [4]
        return answer

class Telegram_Function():
    def __init__(self, chat_id):
        self.chat_id = key.chat_id

    def TelegramSendMsg(self, msg, parse_mode):
        bot.send_message(self.chat_id, msg, parse_mode)
    
    def TelegramSendTable(self, table, parse_mode):
        bot.send_message(self.chat_id, f'<pre>{table}</pre>', parse_mode)
    
    def TelegramSendBalanceTable(self):
        account = GetBalanceTable()
        balancetable = account[0]
        TotalBalance = account[1]
        TotalBalance = round(TotalBalance, 2)
        balance_msg = "<b>Total Balance</b> = " + str(TotalBalance) + emojis.encode(":dollar:")
        bot.send_message(self.chat_id, f'<pre>{balancetable}</pre>', parse_mode=telegram.ParseMode.HTML)
        bot.send_message(self.chat_id, balance_msg, parse_mode=telegram.ParseMode.HTML)


RoseBot()
