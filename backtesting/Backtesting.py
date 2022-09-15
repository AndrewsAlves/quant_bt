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
        self.tradeBookDf = pd.DataFrame()
        
    def addTrade(self, trade) :
        self.tradeList.append(trade)
        
    def addAllTradertoDf(self, merge = False,  tradeList = None):
        
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
        orderStatus = []
        
        if merge : tradeList = tradeList
        else : tradeList = self.tradeList
        
        
        for trade in tradeList:
            
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
            orderStatus.append(trade.orderStatus)
            
            
        dftemplate = {"symbol" : symbol, 
                      "Entry Time" : tradeEntryTime, 
                      "Type" : tradeType,
                      "quantity" : qty,
                      "Entry Price" : entryPrice,
                      "SL price" : stopLossPrice,
                      "Exit Time" : tradeExitTime,
                      "Exit Price" : exitPrice,
                      "Expiry Date" : expiry,
                      "profit" : profits,
                      "orderStatus" : orderStatus}
        
        if merge : self.tradeBookDf.append(dftemplate)
        else : self.tradeBookDf = pd.DataFrame(dftemplate)
        
        
class Trade():
    
    buy = "buy"
    sell = "sell"
    short = "short"
    cover = "cover"
    #orderStatus = ["pending", "executed", "cancelled"]
    
    def __init__(self, tradeId = 0, orderId = 0):
        self.id = tradeId
        self.orderId = orderId
        
        self.symbol = "No Name"
        self.tradeEntryTime = None
        self.tradeType = "None"
        self.qty = 0
        self.entryPrice = 0
        self.expiry = 0
        self.isOptions = False
        self.stopLossPrice = 0
        self.tradeExitTime = None
        self.exitPrice = 0
        self.isOpen = False
        self.orderStatus = 0
        self.profit = 0
        
        
            
        
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
        
        
    def closePosition(self, tradetime, tradetype, exitPrice):
        self.tradeExitTime = tradetime
        self.exitPrice = exitPrice
        if self.tradeType == "short" : self.profit = (self.entryPrice - self.exitPrice) * self.qty
        if self.tradeType == "buy" : self.profit = (self.exitPrice - self.entryPrice) * self.qty    
        
        if exitPrice == 0 : self.profit = 0
        
        self.isOpen = False
            
        
        
        