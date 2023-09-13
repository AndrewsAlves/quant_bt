
"""
Created on Wed Aug 22 15:15:17 2022

###########################################
### 11am STRADLE BACKTESTING BNF  ##########
###########################################


@author: AndyAlves
"""
#%%
import pandas as pd
import talib as ta
import matplotlib.pyplot as plt
import datetime as dt
import os, os.path
from tqdm import tqdm
import math
from backtesting import Backtesting as bt
import traceback
import logging
from backtesting import LocalCsvDatabase as csv_database

# Variables
tf_1Min = "1Min"
tf_5Min = "5Min"
tf_15Min = "15Min"
tf_1H = "H"
tf_1D = "1D"

start_date = '2017-01'
end_date = '2021-12'
O = "Open"
H = "High"
L = "Low"
C = "Close"
bnf_op_path = "G:\\andyvoid\data\quotes\After_cleaned\Banknifty\BNF_options"

mainTradeBook = bt.TradeBook()
tickerDatabase2017_2021 = pd.DataFrame()

#%%
#%%

bnfResampled = csv_database.get_banknifty_data(start_date, end_date, tf_5Min)

#%%

""" 
11am strategy and backtesting section 
Time frame = 5m 
"""

def placeOrder(tickerSymbol, tickerDf, datetime, SLper, LotSize, tradeType, tradeObj = None) :
    if tradeObj == None : 
        tradeObj = bt.Trade()
        tradeObj.tradeId = id(tradeObj)
        
    entryprice = 0
    sl = 0
    orderStatus = 0
    if datetime in tickerDf.index :
        entryprice = tickerDf.loc(axis = 0)[datetime, C]
        sl = entryprice + (entryprice / 100) * SLper
        orderStatus = 1
    else :
        print("Order execution pending, price data not found : " + tickerSymbol + " " , datetime)
    
    tradeObj.openPosition(tickerSymbol, datetime, tradeType, lotSize, entryprice, SLprice = sl, isOptions = True, orderStatus = orderStatus)
    return tradeObj
    

tradeBook = bt.TradeBook()
positions = {}
priceTrackerDf = {}
SLper = 25
lotSize = 25
slippage = 1

for i, row in tqdm(bnfResampled.iterrows(), desc = "Backtesting", total = bnfResampled.shape[0]): 
       
    datentime = row["Date"]
    onlyDate = dt.datetime(datentime.date().year, datentime.date().month, datentime.date().day)
    openP = row[O]
    highP = row[H]
    lowP = row[L]
    closeP = row[C]
    expiryday = False
    
    newday = True
    newday = not(i > 0 and datentime.date().day != bnfResampled.loc[i-1,"Date"].day)
     ## If T = 9 20 open position at the money strike with the stop loss of 25% on each leg 
     ## if T = 15 10 close the remaining positions automatically
           
    strike = str(round(round(closeP,-2)))
    
    
    if newday and datentime.time().hour == 11 and datentime.time().minute == 00 :
        
        #print(tickerSymbol.upper())
        #print("execute straddle")
        tickerSymbolCE = csv_database.getBnfOptionsTickerSymbol(datentime, strike, "CE")
        tickerSymbolPE = csv_database.getBnfOptionsTickerSymbol(datentime, strike, "PE")
        
        CE_df = csv_database.getTicker(datentime, tickerSymbolCE, tf_5Min)
        PE_df = csv_database.getTicker(datentime, tickerSymbolPE, tf_5Min)
        
        """ CE EXECUTION """
        ce_entry = placeOrder(tickerSymbolCE, CE_df, datentime, SLper, lotSize, "short")
                
        """ PE EXECUTION """
        pe_entry = placeOrder(tickerSymbolPE, PE_df, datentime, SLper, lotSize, "short")
        
        """ ADD OPEN POSITIONS TO THE POSITIONS LIST """
        positions[pe_entry.tradeId] = pe_entry
        positions[ce_entry.tradeId] = ce_entry
        
        priceTrackerDf[pe_entry.tradeId] = PE_df
        priceTrackerDf[ce_entry.tradeId] = CE_df

       # print(datentime.time())
        
    """ CLOSE THE ALL POSITIONS IF TIME IS 15:10 and ABOVE"""    
    if datentime.time().hour >= 15 and datentime.time().minute >= 10 and len(positions) != 0 :    
       # print("squared off positions")
        for tradeId in list(positions):
            trade = positions[tradeId]
            
            exitPrice = 0
            if trade.isOpen and trade.orderStatus == 1: 
                if (datentime in priceTrackerDf[tradeId].index):
                    exitPrice = priceTrackerDf[tradeId].loc(axis = 0)[datentime,C]
                else :
                    print("No data available for this datetime so getting the last traded price for that day")
                    startTime = onlyDate.replace(hour = 11, minute = 00)
                    endTime = onlyDate.replace(hour = 15, minute = 25)
                    exitPrice = priceTrackerDf[tradeId].loc(axis = 0)[startTime : endTime, C][-1]
                    
            trade.closePosition(datentime, "cover", exitPrice)
            positions.pop(tradeId)
            priceTrackerDf.pop(tradeId)
            tradeBook.addTrade(trade)
        #print(datentime.time())
        
    """ IF THE TIME IS 11:00 and ABOVE CHECK POSITIONS FOR STOPLOSS AND EXECUTE THE PENDING ORDER """    
    if datentime.time().hour >= 11 and datentime.time().minute > 00 :
        for tradeId in list(positions) :
            trade = positions[tradeId]
            
            """ Check order status and execute the pending order"""
            if trade.orderStatus == 0 and tradeId in priceTrackerDf : 
                placeOrder(trade.symbol, priceTrackerDf[tradeId], datentime, SLper, lotSize, "Short", tradeObj = trade)
                                
            """ Check order status and track the SL price"""
            if trade.orderStatus == 1 and tradeId in priceTrackerDf : 
                
                if not(datentime in priceTrackerDf[tradeId].index):
                    continue
                    
                slprice = trade.stopLossPrice
                barHigh = priceTrackerDf[tradeId].loc(axis = 0)[datentime, H]
                
                if barHigh > slprice : 
                    exitPrice = slprice + slippage
                    trade.closePosition(datentime, "cover", exitPrice)
                    
                    positions.pop(tradeId)
                    priceTrackerDf.pop(tradeId)
                    
                    tradeBook.addTrade(trade)
      

#%%

tradeBook.addAllTradertoDf()
tradeBook.exportTradebookToCSV("11am_straddle_trades.csv")

#%%
backtestedReportDf = tradeBook.tradeBookDf

cumSeries = pd.Series(bt.CumulativeCapital(backtestedReportDf["profit"].tolist(), 100000))
cumSeries.round()
cumSeries.plot()
        


    
    
    
    
 






















