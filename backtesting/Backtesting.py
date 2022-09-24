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
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta 
import matplotlib.pyplot as pp
import plotly.express as pltEx
import plotly.io as pio
pio.renderers.default='browser'


def Cumulative(lists):
    cu_list = []
    length = len(lists)
    cu_list = [sum(lists[0:x:1]) for x in range(0, length+1)]
    roundedCu = [ round(i) for i in cu_list[1:] ]
    return roundedCu

def CumulativeCapital(lists, capital):
    cu_list = []
    length = len(lists)
    cu_list = [capital + sum(lists[0:x:1]) for x in range(0, length+1)]
    roundedCu = [ round(i) for i in cu_list[1:] ]
    return roundedCu
    
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
        exitOrderStatus = []
        
        
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
            exitOrderStatus.append(trade.exitOrderStatus)

            
            
        dftemplate = {"symbol" : symbol, 
                      "Entry Time" : tradeEntryTime, 
                      "Type" : tradeType,
                      "quantity" : qty,
                      "Entry Price" : entryPrice,
                      "SL price" : stopLossPrice,
                      "orderStatus" : orderStatus,
                      "Exit Time" : tradeExitTime,
                      "Exit Price" : exitPrice,
                      "Expiry Date" : expiry,
                      "profit" : profits,
                      "Exit Order Status" : exitOrderStatus }
        
        tradeBooklocal = pd.DataFrame(dftemplate)
        
        if merge : self.tradeBookDf = self.tradeBookDf.append(tradeBooklocal, ignore_index=True)
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
        self.exitOrderStatus = 0
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
        
        if exitPrice == 0 : 
            self.profit = 0
            self.exitOrderStatus = 0
        else :
            self.exitOrderStatus = 1
                
        
        self.isOpen = False
        
        
""" 
//////////////////////////////////////////////////////
///////// BACKTEST BUILDER /////////////////////////
//////////////////////////////////////////////////
"""
            

def getChangePercent(current, previous):
    """ To calcualte the percentage of capital vs total return """
    if current == previous:
        return 0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return float('inf')
    
def CAGR(start, end, periods):
    return ((end/start)**(1/periods)-1) * 100.0

def calculateRunningDrawdown(cum_profit) : 
    # We are going to use a trailing 252 trading day window
    window = 252
    # Calculate the max drawdown in the past window days for each day in the series.
    # Use min_periods=1 if you want to let the first 252 days data have an expanding window
    Roll_Max = cum_profit.rolling(window, min_periods=1).max()
    Daily_Drawdown = (cum_profit/Roll_Max - 1.0)
    
    
    # Next we calculate the minimum (negative) daily drawdown in that window.
    # Again, use min_periods=1 if you want to allow the expanding window
    Max_Daily_Drawdown = Daily_Drawdown.rolling(window, min_periods=1).min()
    
    #Daily_Drawdown.plot()
    #Max_Daily_Drawdown.plot()
    #pp.show()
    
    return Daily_Drawdown

def getWin_LoseRate(tBook) :
    wins = tBook[tBook['profit'] > 0]
    loss = tBook[tBook['profit'] < 0]
    neutral = tBook[tBook['profit'] == 0]
    return [wins.shape[0], loss.shape[0], neutral.shape[0]]

def calculateProfitFactor(tBook) : 
    wins = tBook['profit'].loc[tBook['profit'] > 0].sum()
    loss = tBook['profit'].loc[tBook['profit'] < 0].sum()
    return wins / abs(loss)
    
        
class BacktestReportBuilder :
    
    """ 
    Backtested report 
    
    Start Date *
    End Date *
    Duration *
    Exposure Time 
    Equity Final *
    Equity Peak *
    Total Return [%] *
    Buy & Hold Return (%) 
    com Return (Ann.) (%) *
    STD / Volatality (Ann.) (%) 
    Sharpe Ratio 
    Sortino Ratio 
    Calmar Ratio 
    -Max. Drawdown *
    -Avg. Drawdown 
    -Max. Drawdown Duration 
    Avg. Drawdown Duration 
    -# Trades *
    -Win Rate [%] *
    -Best Trade *
    -Wrost Trade *
    -Avg. Trade *
    -Max Trade Duration *
    -Avg. Trade Duration *
    Profit Factor *
    Expectancy [%]
    SQN
    _Strategy *
    """
    
    
    """ 
    Charts 
    
    Portfolio Equity 
    Drawdown Chart
    Monthly Return and yearly Return Chart
     
    """
    
    def __init__(self,strategyName, btTradeBook = None, startCapital = 200000):
        self.strategyName = strategyName
        self.btTradeBook = btTradeBook
        self.startCapital = startCapital
        
    
    def buildReport(self):
        
        tBook = self.btTradeBook.copy(deep = True)
        
        if tBook.empty:
            print("No trade to backtest!")
            return
        
        tBook['Entry Time'] = pd.to_datetime(tBook['Entry Time'])
        tBook['Exit Time'] = pd.to_datetime(tBook['Exit Time'])

        
        #StartDate
        startDate = tBook["Entry Time"].iloc[0]
        endDate = tBook["Exit Time"].iloc[-1]
        
        #Duration
        durationDelta = endDate - startDate
        
        # find equity final and equity peak   
        tBook['Cum. profits'] =  pd.Series(CumulativeCapital(tBook['profit'].tolist(), self.startCapital))
        equityFinal = tBook['Cum. profits'].iloc[-1]
        equityPeak = tBook['Cum. profits'].max()
        
        #Total return Percent
        returnPer = getChangePercent(equityFinal, self.startCapital)
        
        ## Find compound Annual return
        totalYears = relativedelta(endDate, startDate).years
        compoundAGR = CAGR(self.startCapital, equityFinal, totalYears)
        
        # ## calculate drawdown 
        maximumDrawdownPer = calculateRunningDrawdown(tBook['Cum. profits']).min() * 100.0
        
        maxTradeDurationSr = tBook['Exit Time'] - tBook['Entry Time']
        
        report = {}
        report['strategy'] =  self.strategyName
        report['startdate'] = startDate
        report['enddate'] = endDate
        report['duration'] = durationDelta
        report['equityfinal'] = equityFinal
        report['equitypeak'] = equityPeak
        report['totalreturn'] = returnPer
        report['cagr'] = compoundAGR
        report['max_drawdown'] = maximumDrawdownPer
        report['total_trades'] = tBook.shape[0]
        report['win_trades'] = getWin_LoseRate(tBook)[0]
        report['loss_trades'] = getWin_LoseRate(tBook)[1]
        report['neutral_trades'] = getWin_LoseRate(tBook)[2]
        report['win_per'] = (getWin_LoseRate(tBook)[0] / tBook.shape[0]) * 100.0
        report['loss_per'] = (getWin_LoseRate(tBook)[1] / tBook.shape[0]) * 100.0
        report['best_trade'] =  tBook['profit'].max()
        report['worst_trade'] = tBook['profit'].min()
        report['max_trade_duration'] = maxTradeDurationSr.max()
        report['avg_trade_duration'] = maxTradeDurationSr.mean()
        report['profitfactor'] = calculateProfitFactor(tBook)
        
        
        print("\\\\\\\\\\\\\ BACKTEST REPORT ///////////////")
        print("\n Strategy --- ", self.strategyName)
        print("\n Start Date --- ", startDate)
        print("\n End Date --- ", endDate)
        print("\n duration --- ", durationDelta)
        print("\n Equity Final --- ", equityFinal)
        print("\n Equity Peak --- ", equityPeak)
        print("\n Total Return [%] --- ", returnPer)
        print("\n CAGR [%] --- ", compoundAGR)
        print("\n Max. drawdown [%] --- ", maximumDrawdownPer)
        print("\n Total trades --- ", tBook.shape[0])
        print("\n Win Trades --- ", getWin_LoseRate(tBook)[0])
        print("\n Loss Trades --- ", getWin_LoseRate(tBook)[1])
        print("\n Neutral Trade --- ", getWin_LoseRate(tBook)[2])
        print("\n Win per [%] --- ", (getWin_LoseRate(tBook)[0] / tBook.shape[0]) * 100.0)
        print("\n Loss per [%] --- ", (getWin_LoseRate(tBook)[1] / tBook.shape[0]) * 100.0)
        print("\n Best Trade --- ", tBook['profit'].max())
        print("\n Worst Trade --- ", tBook['profit'].min())
        print("\n Max Trade Duration --- ", maxTradeDurationSr.max())
        print("\n Avg Trade Duration --- ", maxTradeDurationSr.mean())
        print("\n Profit Factor --- ", calculateProfitFactor(tBook))
        
        figEquityCurve = pltEx.line(tBook, x = 'Exit Time', y = 'Cum. profits')
        figEquityCurve.show()
        
        return report





        
        


        
    
        
            
            
    
    
    
    
    
    
    
    
    
    
    
    
        