
"""
Created on Wed Aug 22 15:15:17 2022

###########################################
### 920 STRADLE BACKTESTING BNF  ##########
###########################################

V2 - This version will modify the entry signals 
steps - Sell PE or CE only when either of their stoplosses got hitted


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
bnf_op_path = "D:\\andyvoid\data\quotes\After_cleaned\Banknifty\BNF_options"

mainTradeBook = bt.TradeBook()
tickerDatabase2017_2021 = pd.DataFrame()

#%%
#%%

bnfResampled = csv_database.get_banknifty_data(start_date, end_date, tf_5Min)

#%%

""" 
920 strategy and backtesting section 
Time frame = 5m 
"""

def placeOrder(tickerSymbol, tickerDf, datetime, SL, LotSize, tradeType, tradeObj = None, SLinPer = True) :
    if tradeObj == None : 
        tradeObj = bt.Trade()
        tradeObj.tradeId = id(tradeObj)
        
    entryprice = 0
    sl = 0
    orderStatus = 0
    if datetime in tickerDf.index :
        entryprice = tickerDf.loc(axis = 0)[datetime, "close"]
        sl = SL
        if SLinPer :
            sl = entryprice + (entryprice / 100) * SL
        orderStatus = 1
    else :
        print("Order execution pending, price data not found : " + tickerSymbol + " " , datetime)
    
    tradeObj.openPosition(tickerSymbol, datetime, tradeType, lotSize, entryprice, SLprice = sl, isOptions = True, orderStatus = orderStatus)
    return tradeObj
    

tradeBook = bt.TradeBook()
positions = {}
priceTrackerDf = {}
imaginaryPositions = {}
imaginaryPriceTrackerDf = {}
SLperImg = 25
SLper = 25
lotSize = 25
slippage = 1

for i, row in tqdm(bnfResampled.iterrows(), desc = "Backtesting", total = bnfResampled.shape[0]): 
       
    datentime = row["Date"]
    onlyDate = dt.datetime(datentime.date().year, datentime.date().month, datentime.date().day)
    openP = row["open"]
    highP = row["high"]
    lowP = row["low"]
    closeP = row["close"]
    expiryday = False
    
    newday = True
    newday = not(i > 0 and datentime.date().day != bnfResampled.loc[i-1,"Date"].day)
     ## If T = 9 20 open position at the money strike with the stop loss of 25% on each leg 
     ## if T = 15 10 close the remaining positions automatically
           
    strike = str(round(round(closeP,-2)))
    

       
    
    if newday and datentime.time().hour == 9 and datentime.time().minute == 20 :
        
        #print(tickerSymbol.upper())
        #print("execute straddle")
        tickerSymbolCE = csv_database.getBnfOptionsTickerSymbol(datentime, strike, "CE")
        tickerSymbolPE = csv_database.getBnfOptionsTickerSymbol(datentime, strike, "PE")
        
        CE_df = csv_database.getTicker(datentime, tickerSymbolCE, tf_5Min)
        PE_df = csv_database.getTicker(datentime, tickerSymbolPE, tf_5Min)
        
        """ CE EXECUTION """
        imaginary_ce_entry = placeOrder(tickerSymbolCE, CE_df, datentime, SLperImg, lotSize, "short")
                
        """ PE EXECUTION """
        imaginary_pe_entry = placeOrder(tickerSymbolPE, PE_df, datentime, SLperImg, lotSize, "short")
        
        """ ADD OPEN POSITIONS TO THE POSITIONS LIST """
        imaginaryPositions[imaginary_pe_entry.tradeId] = imaginary_pe_entry
        imaginaryPositions[imaginary_ce_entry.tradeId] = imaginary_ce_entry
        
        imaginaryPriceTrackerDf[imaginary_pe_entry.tradeId] = PE_df
        imaginaryPriceTrackerDf[imaginary_ce_entry.tradeId] = CE_df

       # print(datentime.time())
        
    """ CLOSE THE ALL POSITIONS IF TIME IS 15:10 and ABOVE"""    
    if datentime.time().hour >= 15 and datentime.time().minute >= 10 and len(positions) != 0 :    
       # print("squared off positions")
        for tradeId in list(positions):
            trade = positions[tradeId]
            
            exitPrice = 0
            if trade.isOpen and trade.orderStatus == 1: 
                if (datentime in priceTrackerDf[tradeId].index):
                    exitPrice = priceTrackerDf[tradeId].loc(axis = 0)[datentime,"close"]
                else :
                    print("\n Entry Time - ", trade.tradeEntryTime)
                    print("\n No data available for this datetime so getting the last traded price for that day ")
                    print("\n Missing data " + str(datentime) + " " + trade.symbol)
                    startTime = onlyDate.replace(hour = 9, minute = 15)
                    endTime = onlyDate.replace(hour = 15, minute = 25)
                    exitPrice = priceTrackerDf[tradeId][startTime : endTime]["close"].iloc[-1]
                    
            trade.closePosition(datentime, "cover", exitPrice)
            positions.pop(tradeId)
            priceTrackerDf.pop(tradeId)
            tradeBook.addTrade(trade)
        #print(datentime.time())
        
    """ IF THE TIME IS 9:20 AND ABOVE CHECK FOR THE IMAGINARY POSITIONS STOLOSS AND TRIGGER AN ORDER TO EXECUTE """        
    
    if datentime.time().hour >= 9 and datentime.time().minute > 20 :
        
        # Tracking for imagineryPostions whether SL hit to open a real position.
        for tradeId in list(imaginaryPositions) :
            
            trade = imaginaryPositions[tradeId]
            
            if tradeId in imaginaryPriceTrackerDf : 
                
                if not(datentime in imaginaryPriceTrackerDf[tradeId].index):
                    continue
                    
                slprice = trade.stopLossPrice
                barHigh = imaginaryPriceTrackerDf[tradeId].loc(axis = 0)[datentime, "high"]
                
                if barHigh > slprice : 
                    
                    """ EXECUTE THE TRADE IF IMAGINERY STOPLOSS IS HIT """
                    
                    if "PE" in trade.symbol : 
                        tickerSymbolCE = csv_database.getBnfOptionsTickerSymbol(datentime, strike, "CE")
                        CE_df = csv_database.getTicker(datentime, tickerSymbolCE, tf_5Min)
                        
                        dateT = onlyDate.replace(hour = 9, minute = 20)
                        if dateT in CE_df.index :
                            imagineryEntryPrice = CE_df.loc[dateT,'close']
                            sl = imagineryEntryPrice + (imagineryEntryPrice / 100) * SLper
                            ce_entry = placeOrder(tickerSymbolCE, CE_df, datentime, sl, lotSize, "short", SLinPer = False)
                        else :
                            print("SL order pending, price data not found : " + tickerSymbolCE + " " , dateT)
                            ce_entry = placeOrder(tickerSymbolCE, CE_df, datentime, sl, lotSize, "short")

                        positions[ce_entry.tradeId] = ce_entry
                        priceTrackerDf[ce_entry.tradeId] = CE_df
                        
                    if "CE" in trade.symbol :
                        
                        tickerSymbolPE = csv_database.getBnfOptionsTickerSymbol(datentime, strike, "PE")
                        PE_df = csv_database.getTicker(datentime, tickerSymbolPE, tf_5Min)
                        
                        dateT = onlyDate.replace(hour = 9, minute = 20)
                        if dateT in CE_df.index :
                            imagineryEntryPrice = PE_df.loc[dateT,'close']
                            sl = imagineryEntryPrice + (imagineryEntryPrice / 100) * SLper
                            pe_entry = placeOrder(tickerSymbolCE, PE_df, datentime, sl, lotSize, "short", SLinPer = False)
                        else :
                            print("SL order pending, price data not found : " + tickerSymbolCE + " " , dateT)
                            pe_entry = placeOrder(tickerSymbolCE, PE_df, datentime, sl, lotSize, "short")
                        
                        positions[pe_entry.tradeId] = pe_entry
                        priceTrackerDf[pe_entry.tradeId] = PE_df
                        
                    imaginaryPositions.clear()
                    imaginaryPriceTrackerDf.clear()
                    
                    break

        """IF THE TIME IS 9:20 and ABOVE CHECK POSITIONS FOR STOPLOSS AND EXECUTE THE PENDING ORDER """    

        for tradeId in list(positions) :
            trade = positions[tradeId]
            
            """ Check order status and execute the pending order"""
            if trade.orderStatus == 0 and tradeId in priceTrackerDf : 
                placeOrder(trade.symbol, priceTrackerDf[tradeId], datentime, SLper, lotSize, "short", tradeObj = trade)
                                
            """ Check order status and track the SL price"""
            if trade.orderStatus == 1 and tradeId in priceTrackerDf : 
                
                if not(datentime in priceTrackerDf[tradeId].index):
                    continue
                    
                slprice = trade.stopLossPrice
                barHigh = priceTrackerDf[tradeId].loc(axis = 0)[datentime, "high"]
                
                if barHigh > slprice : 
                    exitPrice = slprice + slippage
                    trade.closePosition(datentime, "cover", exitPrice)
                    
                    positions.pop(tradeId)
                    priceTrackerDf.pop(tradeId)
                    
                    tradeBook.addTrade(trade)
      

#%%

tradeBook.addAllTradertoDf()
tradeBook.exportTradebookToCSV("920_straddle_v2_trades.csv")

#%%
backtestedReportDf = tradeBook.tradeBookDf

cumSeries = pd.Series(bt.CumulativeCapital(backtestedReportDf["profit"].tolist(), 200000))
cumSeries.round()
cumSeries.plot()
        


    
    
    
    
 






















