#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  9 19:30:20 2022

@author: andrewsalves

Back tested trader orders modules 

This module stores all the traders takes place in the backtesting process 

It can produce all the Information about Equity reports

"""

import os
import pandas as pd
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta 
from tabulate import tabulate
from Utilities import StaticVariables as statics

import plotly.express as pltEx
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.io as pio
from plotly.colors import n_colors

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
        self.missingData = pd.DataFrame()
    
    def getTradeBook(self) : return self.tradeBookDf

    
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
        
        
    def exportTradebookToCSV(self,fileId, strategyName) :
        self.tradeBookDf.to_csv(statics.tradeListPath + "\\" + fileId + "_" + strategyName + '.csv')
        self.missingData.to_csv(statics.tradeListPath + "\\" + fileId + "_MissingData.csv")
        
    def generateReport(self,symbol, StrategyName, capital, daysList = [], onlyExpiryDays = False) : 
        self.addAllTradertoDf()
        btreprotBuilder = BacktestReportBuilder(symbol, StrategyName, btTradeBook = self.tradeBookDf, 
                                                startCapital = capital, 
                                                daysList = daysList,
                                                onlyExpiryDays = onlyExpiryDays)
        report, dailyReturn, monthlyReturn, yeatlyReturnDf = btreprotBuilder.buildReport()
        return report, report, dailyReturn
        
        
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
        if self.tradeType == "short" : 
            pnl = (self.entryPrice - self.exitPrice) * self.qty
            self.profit = round(pnl, 2)
        if self.tradeType == "buy" : 
            pnl = (self.exitPrice - self.entryPrice) * self.qty    
            self.profit = round(pnl, 2)

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
    
    return Daily_Drawdown * 100

def getWin_LoseRate(tBook) :
    wins = tBook[tBook['profit'] > 0]
    loss = tBook[tBook['profit'] < 0]
    neutral = tBook[tBook['profit'] == 0]
    return [wins.shape[0], loss.shape[0], neutral.shape[0]]

def calculateProfitFactor(tBook) : 
    wins = tBook['profit'].loc[tBook['profit'] > 0].sum()
    loss = tBook['profit'].loc[tBook['profit'] < 0].sum()
    return wins / abs(loss)

def getOnlyExpiryDayTrades(tBook, symbol) : 
    
    symbolDf = pd.read_csv(statics.path_db + "\\" + symbol + "\\options\\" + "option_symbols.csv")
    symbolDf['Expiry Date'] = pd.to_datetime(symbolDf['Expiry Date'])
    
    tBook['Entry Time'] = pd.to_datetime(tBook['Entry Time'])
    tBook['Exit Time'] = pd.to_datetime(tBook['Exit Time'])

    expiryDayList = []
    for i, row in tBook.iterrows() : 
        Date = row['Entry Time'].replace(hour=0, minute=0)
        if Date in symbolDf['Expiry Date'].values:
            expiryDayList.append("yes")
        else : 
            expiryDayList.append("no")
        
    tBook['expiry'] = pd.Series(expiryDayList)
    tBook['day'] = tBook['Entry Time'].dt.day_name()
    tBookOnlyExpiry = tBook[tBook['expiry'] == "yes"]
    
    tBookOnlyExpiry.reset_index(inplace = True)
    tBookOnlyExpiry = tBookOnlyExpiry.drop('index', axis=1)

    return tBookOnlyExpiry

def getOnlyTheDays(tBook, dayList = []) : 
    
    daysDf = None
    portfolioDayWise = tBook.groupby(tBook['Entry Time'].dt.day_name())
    
    for day in dayList : 
        dayDf = portfolioDayWise.get_group(day)
        if daysDf is None :
            daysDf = dayDf
        else :
            daysDf =  pd.concat([daysDf, dayDf])
                    
    daysDf['Entry Time'] = pd.to_datetime(daysDf['Entry Time'])
    daysDf['Exit Time'] = pd.to_datetime(daysDf['Exit Time'])        

    daysDf = daysDf.sort_values(by = 'Entry Time', axis=0, ascending=True)
    daysDf.reset_index(inplace = True)
    daysDf = daysDf.drop('index', axis=1)
    
    return daysDf
    
        
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
    
    def __init__(self,symbol,strategyName, btTradeBook = None, startCapital = 200000, compoundProfits = False,daysList = [], onlyExpiryDays = False):
        self.symbol = symbol
        self.strategyName = strategyName
        self.btTradeBook = btTradeBook
        self.startCapital = startCapital
        self.compoundProfits = compoundProfits
        self.onlyDays = daysList
        self.onlyExpiryDays = onlyExpiryDays
        
    
    def buildReport(self):
        
        tBook = self.btTradeBook.copy(deep = True)
        
        if tBook.empty:
            print("No trade to backtest!")
            return
        
        if len(self.onlyDays) == 0 :
             if self.onlyExpiryDays : 
                 tBook = getOnlyExpiryDayTrades(tBook, self.symbol)
        else :
             tBook = getOnlyTheDays(tBook, self.onlyDays)
        
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
        ## check if total years less than a year
        if (totalYears == 0) :
            totalYears = 1            
        compoundAGR = CAGR(self.startCapital, equityFinal, totalYears)
        
        # ## calculate drawdown 
        maximumDrawdownPer = calculateRunningDrawdown(tBook['Cum. profits']).min() * 100.0
        maxTradeDurationSr = tBook['Exit Time'] - tBook['Entry Time']
        
        
        # finding returns for months and years
        dateAndProfitDf = pd.DataFrame()
        dateAndProfitDf['Date'] = tBook['Exit Time']
        dateAndProfitDf['profit'] = tBook['profit']
        dateAndProfitDf['Cum. profits'] = tBook['Cum. profits']
        
        dailyReturnsDf = dateAndProfitDf.groupby(pd.Grouper(key='Date', axis=0, freq='D')).sum()
        dailyReturnsDf['Cum. profits'] = dateAndProfitDf[['Date','Cum. profits']].groupby(pd.Grouper(key='Date', axis=0, freq='D')).last()
        dailyReturnsDf.reset_index(inplace = True)
        
        portfolioDayWisePnl = dailyReturnsDf.groupby(dailyReturnsDf['Date'].dt.day_name()).sum()

        monthlyReturnsDf = dateAndProfitDf.groupby(pd.Grouper(key='Date', axis=0, freq='M')).sum()
        monthlyReturnsDf['Cum. profits'] = dateAndProfitDf[['Date','Cum. profits']].groupby(pd.Grouper(key='Date', axis=0, freq='M')).last()

        yearlyReturnsDf = dateAndProfitDf.groupby(pd.Grouper(key='Date', axis=0, freq='Y')).sum()
        yearlyReturnsDf['Cum. profits'] = dateAndProfitDf[['Date','Cum. profits']].groupby(pd.Grouper(key='Date', axis=0, freq='Y')).last()

        # monthly & Yearly return percentage compared with previous cumulative profit or starting capital
        if self.compoundProfits : 
            print('find cumulative compound percentage')
        else :
            monthlyReturnsDf['Com. per'] = monthlyReturnsDf['profit'] / (self.startCapital / 100.0)
            yearlyReturnsDf['Com. per'] = yearlyReturnsDf['profit'] / (self.startCapital / 100.0)

        report = {}
        report['strategy'] =  self.strategyName
        report['starting Capital'] =  self.startCapital
        report['compount profits'] = self.compoundProfits
        report['startdate'] = str(startDate)
        report['enddate'] = str(endDate)
        report['duration'] = str(durationDelta)
        report['equityfinal'] = equityFinal
        report['equitypeak'] = equityPeak
        report['totalreturn'] = round(returnPer, 2)
        report['cagr'] = round(compoundAGR, 2)
        report['max_drawdown'] = round(maximumDrawdownPer, 2)
        report['total_trades'] = tBook.shape[0]
        report['win_trades'] = getWin_LoseRate(tBook)[0]
        report['loss_trades'] = getWin_LoseRate(tBook)[1]
        report['neutral_trades'] = getWin_LoseRate(tBook)[2]
        report['win_per'] = round((getWin_LoseRate(tBook)[0] / tBook.shape[0]) * 100.0, 2)
        report['loss_per'] = round((getWin_LoseRate(tBook)[1] / tBook.shape[0]) * 100.0, 2)
        report['best_trade'] =  tBook['profit'].max()
        report['worst_trade'] = tBook['profit'].min()
        report['max_trade_duration'] = maxTradeDurationSr.max()
        report['avg_trade_duration'] = maxTradeDurationSr.mean()
        report['profitfactor'] = round(calculateProfitFactor(tBook), 2)
        
        # Day wise Analysis
        dayWiseReport = {}
        dayWiseReport['Best Day'] = dailyReturnsDf['profit'].max()
        dayWiseReport['Worst Day'] = dailyReturnsDf['profit'].min()
        dayWiseReport['Total Win Days'] = getWin_LoseRate(dailyReturnsDf)[0]
        dayWiseReport['Total Loss Days'] = getWin_LoseRate(dailyReturnsDf)[1]

        reportDf = pd.DataFrame(report.items(), columns=['Parameters', 'Result'])
        dayWiseReportDf = pd.DataFrame(dayWiseReport.items(), columns=['Parameters', 'Result'])
        
        dayWiseReportDf = dayWiseReportDf.round(2)
        yearlyReturnsDf = yearlyReturnsDf.round(2)
        monthlyReturnsDf = monthlyReturnsDf.round(2)

        
        print("\\\\\\\\\\\\\ BACKTEST REPORT ///////////////")
        print(tabulate(report.items(), headers = ['Parameters', 'Result'], tablefmt='grid'))
        print("\\\\\\\\\\\\\ DAY WISE REPORT ///////////////")
        print(tabulate(dayWiseReport.items(), headers = ['Parameters', 'Result'], tablefmt='grid'))
        print("\n\\\\\\\\\\\\\ YEARLY RETURNS ///////////////")
        print(tabulate(yearlyReturnsDf, headers = ['Date', 'Profits', 'Cum. Profit', 'Cum. Profit %'], tablefmt='grid'))
        print("\n\\\\\\\\\\\\\ MONTHLY RETURNS ///////////////")
        print(tabulate(monthlyReturnsDf, headers = ['Date', 'Profits', 'Cum. Profit', 'Cum. Profit %'], tablefmt='grid'))
       
        
        # print("\\\\\\\\\\\\\ BACKTEST REPORT ///////////////")
        # print("\n Strategy --- ", self.strategyName)
        # print("\n starting Capital --- ", self.startCapital)
        # print("\n Compount profits? --- ", self.compoundProfits)
        # print("\n Start Date --- ", startDate)
        # print("\n End Date --- ", endDate)
        # print("\n duration --- ", durationDelta)
        # print("\n Equity Final --- ", equityFinal)
        # print("\n Equity Peak --- ", equityPeak)
        # print("\n Total Return [%] --- ", returnPer)
        # print("\n CAGR [%] --- ", compoundAGR)
        # print("\n Max. drawdown [%] --- ", maximumDrawdownPer)
        # print("\n Total trades --- ", tBook.shape[0])
        # print("\n Win Trades --- ", getWin_LoseRate(tBook)[0])
        # print("\n Loss Trades --- ", getWin_LoseRate(tBook)[1])
        # print("\n Neutral Trade --- ", getWin_LoseRate(tBook)[2])
        # print("\n Win per [%] --- ", (getWin_LoseRate(tBook)[0] / tBook.shape[0]) * 100.0)
        # print("\n Loss per [%] --- ", (getWin_LoseRate(tBook)[1] / tBook.shape[0]) * 100.0)
        # print("\n Best Trade --- ", tBook['profit'].max())
        # print("\n Worst Trade --- ", tBook['profit'].min())
        # print("\n Max Trade Duration --- ", maxTradeDurationSr.max())
        # print("\n Avg Trade Duration --- ", maxTradeDurationSr.mean())
        # print("\n Profit Factor --- ", calculateProfitFactor(tBook))
        
        #/////////////////////////////
    
        # figEquityCurve = pltEx.line(tBook, x = 'Exit Time', y = 'Cum. profits')
        # figEquityCurve.show()
    
        # figDrawdown = pltEx.line(runningDrawdownDf, x = 'Date', y = 'drawdown')
        # figDrawdown.show()
        
        # figDailyReturn = pltEx.bar(dailyReturnsDf, x = dailyReturnsDf.index, y = 'profit')
        # figDailyReturn.show()
        
        
        
        #//////////////////////////////////// TABLE LAYOUT ////////////////
        
        headerColor = pltEx.colors.qualitative.Dark24[5]
        cellColor = pltEx.colors.qualitative.Pastel2[7]    
        
        fig = make_subplots(
            rows=2, cols=2,
            shared_xaxes=True,
            vertical_spacing=0.01,
            horizontal_spacing=0.01,
            specs=[[{"type": "table"}, {"type": "table"}],[ {"type": "table"}, {"type": "table"}]]
        )
        
        fig.add_trace(go.Table(header=dict(values=list(reportDf.columns), fill_color= headerColor, align='left',font=dict(color='White')),
                               cells=dict(values=[reportDf['Parameters'], 
                                                  reportDf['Result'].astype(str)], 
                                          fill_color= cellColor,
                                          align='left')),
                      row=1, col=1)
        
        fig.add_trace(go.Table(header=dict(values=list(dayWiseReportDf.columns), fill_color=headerColor, align='left',font=dict(color='White')),
                               cells=dict(values=[dayWiseReportDf['Parameters'], 
                                                  dayWiseReportDf['Result']], 
                                          fill_color= cellColor, 
                                          align='left')),
                      row=2, col=1)
        
        columnList = list(monthlyReturnsDf.columns)
        columnList.insert(0, 'Date')
        print(columnList)
        
        fig.add_trace(go.Table(header=dict(values= columnList, fill_color=headerColor, align='left', font=dict(color='White')),
                               cells=dict(values=[yearlyReturnsDf.index.astype(str), 
                                                  yearlyReturnsDf['profit'],
                                                  yearlyReturnsDf['Cum. profits'],
                                                  yearlyReturnsDf['Com. per']], 
                                          fill_color= cellColor, 
                                          align='left')),
                      row=1, col=2)
        
        fig.add_trace(go.Table(header=dict(values= columnList, fill_color=headerColor, align='left', font=dict(color='White')),
                               cells=dict(values=[monthlyReturnsDf.index.astype(str), 
                                                  monthlyReturnsDf['profit'],
                                                  monthlyReturnsDf['Cum. profits'],
                                                  monthlyReturnsDf['Com. per']], 
                                          fill_color= cellColor,
                                          align='left')),
                      row=2, col=2)
    
        fig.update_layout(
            showlegend=False,
            title_text= self.strategyName + " Report",
        )
    
                                        
                                        # Plot the figure
        fig.show()
        
        #//////////////////////////////// CHART LAYOUT //////////////////
        
        runningDrawdownDf = pd.DataFrame()
        runningDrawdownDf['drawdown'] = calculateRunningDrawdown(tBook['Cum. profits'])
        runningDrawdownDf['Date'] = tBook['Exit Time']
        
        figCharts = make_subplots(rows=4, cols=1)
        figCharts.append_trace(go.Scatter(x=tBook['Exit Time'], y=tBook['Cum. profits'],
                    mode='lines+markers',
                    name='Cum. Profits'), row=1, col=1)
                            
        figCharts.append_trace(go.Scatter(x= runningDrawdownDf['Date'], y=runningDrawdownDf['drawdown'],
                    mode='lines+markers',
                    name='Cum. Drawdown'), row=2, col=1)
        
        figCharts.append_trace(go.Scatter(x= dailyReturnsDf['Date'], y= dailyReturnsDf['profit'],
                    mode='lines+markers',
                    name='Daily PnL'), row=3, col=1)
        
        figCharts.append_trace(go.Bar(x = portfolioDayWisePnl.index, y = portfolioDayWisePnl['profit'],
                    name='Day wise total PnL'), row=4, col=1)
        
        figCharts.update_layout(title_text="Charts", autosize = True, height = 900*4)
        figCharts.update_xaxes(rangeslider=dict(visible=False)) 
        figCharts.show()
        
        return tBook, dailyReturnsDf, monthlyReturnsDf, yearlyReturnsDf





        
        


        
    
        
            
            
    
    
    
    
    
    
    
    
    
    
    
    
        