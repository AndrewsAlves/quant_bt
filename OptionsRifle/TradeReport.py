# -*- coding: utf-8 -*-
"""
Created on Sat May  6 21:10:18 2023
@author: Andy Void
"""

""" 
//////////////////////////////////////////////////////
///////// Trades Report BUILDER /////////////////////////
//////////////////////////////////////////////////
"""
            
import pandas as pd
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta 
from tabulate import tabulate


import plotly.express as pltEx
from plotly.subplots import make_subplots
import plotly.graph_objects as go
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
    wins = tBook[tBook['pnl'] > 0]
    loss = tBook[tBook['pnl'] < 0]
    neutral = tBook[tBook['pnl'] == 0]
    return [wins.shape[0], loss.shape[0], neutral.shape[0]]

def calculateProfitFactor(tBook) : 
    wins = tBook['pnl'].loc[tBook['pnl'] > 0].sum()
    loss = tBook['pnl'].loc[tBook['pnl'] < 0].sum()
    return wins / abs(loss)

def calculateCharges(tBook) : 
    charges = pd.DataFrame()
    charges['entry_charge'] = ((tBook['qty'] * tBook['entry_price'] / 100)  * 0.05) + 20
    charges['entry_charge'] = ((charges['entry_charge'] / 100) * 18) + charges['entry_charge']
    charges['exit_charge'] = ((tBook['qty'] * tBook['exit_price'] / 100)  * 0.05) + ((tBook['qty'] * tBook['exit_price'] / 100)  * 0.0625) + 20
    charges['exit_charge'] = ((charges['exit_charge'] / 100) * 18) + charges['exit_charge']
    print(charges['entry_charge'])
    print(charges['exit_charge'])
    charges['total_charge'] = charges['entry_charge'] + charges['exit_charge']
    return charges['total_charge']
    
class TradeReportBuilder :
    
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
    
    def __init__(self,strategyName, btTradeBook = None, startCapital = 200000, compoundProfits = False):
        self.strategyName = strategyName
        self.btTradeBook = btTradeBook
        self.startCapital = startCapital
        self.compoundProfits = compoundProfits
        
    
    def buildReport(self):
        
        tBook = self.btTradeBook.copy(deep = True)
        
        if tBook.empty:
            print("No trade to backtest!")
            return
        
        tBook['entry_time'] = pd.to_datetime(tBook['entry_time'])
        tBook['exit_time'] = pd.to_datetime(tBook['exit_time'])

        
        #StartDate
        startDate = tBook["entry_time"].iloc[0]
        endDate = tBook["exit_time"].iloc[-1]
        
        #Duration
        durationDelta = endDate - startDate
        
        #Total no of traded days
        df = pd.DataFrame()
        df['trade_dates'] = tBook['entry_time'].dt.date
        unique_dates = df['trade_dates'].nunique()
        
        #Avg. trades per day
        avgTradesPerDay = df['trade_dates'].value_counts().mean()
        
        #Calculate Avg profit and loss per trade 
        avgProfitandLoss = pd.DataFrame()
        avgPnl = tBook['pnl']
        avgPnl = avgPnl.reset_index(drop=True)
        avgProfitandLoss['profit_trades'] = avgPnl[avgPnl > 0]
        avgProfitandLoss['loss_trades'] = avgPnl[avgPnl < 0]
        
        # find equity final and equity peak   
        tBook['Cum. profits'] =  pd.Series(CumulativeCapital(tBook['pnl'].tolist(), self.startCapital))
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
        
        maxTradeDurationSr = tBook['exit_time'] - tBook['entry_time']
        
        tBook['charges'] = calculateCharges(tBook)
    
        totalcharges = tBook['charges'].sum()
        
        # finding returns for months and years
        dateAndProfitDf = pd.DataFrame()
        dateAndProfitDf['Date'] = tBook['exit_time']
        dateAndProfitDf['profits'] = tBook['pnl']
        #dateAndProfitDf['Cum. profits'] = tBook['Cum. profits']
        
        dailyReturnsDf = dateAndProfitDf.groupby(pd.Grouper(key='Date', axis=0, freq='D')).sum()
        #dailyReturnsDf['Cum. profits'] = dateAndProfitDf[['Date','Cum. profits']].groupby(pd.Grouper(key='Date', axis=0, freq='D')).last()
        
        monthlyReturnsDf = dateAndProfitDf.groupby(pd.Grouper(key='Date', axis=0, freq='M')).sum()
        #monthlyReturnsDf['Cum. profits'] = dateAndProfitDf[['Date','Cum. profits']].groupby(pd.Grouper(key='Date', axis=0, freq='M')).last()

        yearlyReturnsDf = dateAndProfitDf.groupby(pd.Grouper(key='Date', axis=0, freq='Y')).sum()
        #yearlyReturnsDf['Cum. profits'] = dateAndProfitDf[['Date','Cum. profits']].groupby(pd.Grouper(key='Date', axis=0, freq='Y')).last()

        # monthly & Yearly return percentage compared with previous cumulative profit or starting capital
        if self.compoundProfits : 
            print('find cumulative compound percentage')
        else :
            monthlyReturnsDf['Com. per'] = monthlyReturnsDf['profits'] / (self.startCapital / 100.0)
            yearlyReturnsDf['Com. per'] = yearlyReturnsDf['profits'] / (self.startCapital / 100.0)

        report = {}
        report['strategy'] =  self.strategyName
        report['starting Capital'] =  self.startCapital
        report['compount profits'] = self.compoundProfits
        report['startdate'] = startDate
        report['enddate'] = endDate
        report['duration'] = durationDelta
        report['No. of days traded'] = unique_dates
        report['equityfinal'] = self.startCapital + tBook['pnl'].sum()
        report['equitypeak'] = equityPeak
        report['totalreturn'] = returnPer
        report['cagr'] = compoundAGR
        report['max_drawdown'] = maximumDrawdownPer
        report['total_trades'] = tBook.shape[0]
        report['avg. trades per day'] = avgTradesPerDay
        report['win_trades'] = getWin_LoseRate(tBook)[0]
        report['loss_trades'] = getWin_LoseRate(tBook)[1]
        report['neutral_trades'] = getWin_LoseRate(tBook)[2]
        report['win_per'] = (getWin_LoseRate(tBook)[0] / tBook.shape[0]) * 100.0
        report['loss_per'] = (getWin_LoseRate(tBook)[1] / tBook.shape[0]) * 100.0
        report['best_trade'] =  tBook['pnl'].max()
        report['worst_trade'] = tBook['pnl'].min()
        report['avg. profit in wins'] = avgProfitandLoss['profit_trades'].mean()
        report['avg. loss in loss'] = avgProfitandLoss['loss_trades'].mean()
        report['max_trade_duration'] = maxTradeDurationSr.max()
        report['avg_trade_duration'] = maxTradeDurationSr.mean()
        report['profitfactor'] = calculateProfitFactor(tBook)
        report['Brokerage and charges'] = totalcharges
        
        print("\\\\\\\\\\\\\ BACKTEST REPORT ///////////////")
        print(tabulate(report.items(), headers = ['Parameters', 'Result'], tablefmt='grid'))
        print("\n\\\\\\\\\\\\\ YEARLY RETURNS ///////////////")
        print(tabulate(yearlyReturnsDf, headers = ['Date', 'Profits', 'Cum. Profit %'], tablefmt='grid'))
        print("\n\\\\\\\\\\\\\ MONTHLY RETURNS ///////////////")
        print(tabulate(monthlyReturnsDf, headers = ['Date', 'Profits', 'Cum. Profit %'], tablefmt='grid'))
       
        
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
        
        
        figEquityCurve = pltEx.line(tBook, x = 'exit_time', y = 'Cum. profits')
        figEquityCurve.show()
        
        runningDrawdownDf = pd.DataFrame()
        runningDrawdownDf['drawdown'] = calculateRunningDrawdown(tBook['Cum. profits'])
        runningDrawdownDf['Date'] = tBook['exit_time']
        
        figDrawdown = pltEx.line(runningDrawdownDf, x = 'Date', y = 'drawdown')
        figDrawdown.show()
        
        figDailyReturn = pltEx.bar(dailyReturnsDf, x = dailyReturnsDf.index, y = 'profits')
        figDailyReturn.show()
        
        return report, dailyReturnsDf, monthlyReturnsDf, yearlyReturnsDf, avgProfitandLoss





