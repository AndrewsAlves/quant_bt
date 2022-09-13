#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  9 19:30:20 2022

@author: andrewsalves

Back tested trader orders modules 

This module stores all the traders takes place in the backtesting process 

It can produce all the Information about Equity reports


"""

import pandas as pd
import datetime as dt


def Cumulative(lists):
    cu_list = []
    length = len(lists)
    cu_list = [sum(lists[0:x:1]) for x in range(0, length+1)]
    return cu_list[1:]
    
class TradeBook(): 
    
    
    def __init__(self):
        self.tradeList = []
        self.tradeDf = pd.DataFrame()
        
    def addTrade(self, trade) :
        self.tradeList.append(trade)
        
    def addAllTradertoDf(self):
        
        symbol = []
        tradeEntryTime = []
        tradeType = []
        qty = []
        entryPrice = []
        expiry = []
        stopLossPrice = []
        tradeExitTime = []
        exitPrice = []
        profits = []
        
        for trade in self.tradeList:
            
            symbol.append(trade.symbol)
            tradeEntryTime.append(trade.tradeEntryTime)
            tradeType.append(trade.tradeType)
            qty.append(trade.qty)
            entryPrice.append(trade.entryPrice)
            stopLossPrice.append(trade.stopLossPrice)
            tradeExitTime.append(trade.tradeExitTime)
            exitPrice.append(trade.exitPrice)
            expiry.append(trade.expiry)
            profits.append(trade.profit)
            
            dftemplate = {"symbol" : symbol, 
                          "Entry Time" : tradeEntryTime, 
                          "Type" : tradeType,
                          "quantity" : qty,
                          "Entry Price" : entryPrice,
                          "SL price" : stopLossPrice,
                          "Exit Time" : tradeExitTime,
                          "Exit Price" : exitPrice,
                          "Expiry Date" : expiry,
                          "profit" : profits}
            
        self.tradeDf = pd.DataFrame(dftemplate)
        


class Trade():
    
    buy = "buy"
    sell = "sell"
    short = "short"
    cover = "cover"
    #orderStatus = ["pending", "executed", "cancelled"]
    
    def __init__(self, tradeId = 0, orderId = 0):
        self.id = tradeId
        self.orderId = orderId
            
        
    def openPosition(self, symbol, tradetime, tradetype, qty = 0, price = 0, expiry = 0, isOptions = False, SLprice = 0, orderStatus = "pending"):
        self.symbol = symbol
        self.tradeEntryTime = tradetime
        self.tradeType = tradetype
        self.qty = qty
        self.entryPrice = price
        self.expiry = expiry
        self.isOptions = isOptions
        self.stopLossPrice = SLprice
        self.isOpen = True
        self.orderStatus = orderStatus
        
    def setStopLoss(self, SLprice): 
        self.stopLossPrice = SLprice
        
        
    def closePosition(self, tradetime, tradetype, price):
        self.tradeExitTime = tradetime
        self.exitPrice = price
        if self.tradeType == "short" : self.profit = (self.entryPrice - self.exitPrice) * self.qty
        if self.tradeType == "buy" : self.profit = (self.exitPrice - self.entryPrice) * self.qty    
        self.isOpen = False
            
        
        
        