
"""
Created on Wed Aug 22 15:15:17 2022

#############################################
### BANKNIFTY EXPIRY DAY STRATEGY  ##########
############################################

Logic 
# Sell a 920 straddle 
# Sell Open range 

@author: AndyAlves
"""
#%%
import pandas as pd
import datetime as dt
from tqdm import tqdm
from backtesting import Backtesting as bt
from backtesting import LocalCsvDatabase as csv_database

# Variables
tf_1Min = "1Min"
tf_5Min = "5Min"
tf_15Min = "15Min"
tf_1H = "H"
tf_1D = "1D"

start_date = '2017-01'
end_date = '2017-12'
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
920 strategy and backtesting section 
Time frame = 5m 
"""

def placeOrder(tickerSymbol, tickerDf, datetime, SL, LotSize, tradeType, tradeObj = None, isSLper = True) :
    if tradeObj == None : 
        tradeObj = bt.Trade()
        tradeObj.tradeId = id(tradeObj)
        
    entryprice = 0
    sl = 0
    orderStatus = 0
    if datetime in tickerDf.index :
        entryprice = tickerDf.loc(axis = 0)[datetime, "Close"]
        if isSLper : sl = entryprice + (entryprice / 100) * SL
        else : sl = SL
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
bnfOptionsTickerDb = csv_database.getBnfOptionsTickerDb()
bnfOptionsExpiryDates = bnfOptionsTickerDb['Expiry Date'].drop_duplicates(keep = "first")
bnfOptionsExpiryDates.reset_index(inplace = True, drop = True)

def isOptionsExpiryDay(datetime) : 
    onlyDate = dt.datetime(datetime.date().year, datetime.date().month, datetime.date().day)
    isExpiryday = onlyDate in bnfOptionsExpiryDates.tolist()
    return isExpiryday

for i, row in tqdm(bnfResampled.iterrows(), desc = "Backtesting", total = bnfResampled.shape[0]): 
       
    datentime = row["Date"]
    onlyDate = dt.datetime(datentime.date().year, datentime.date().month, datentime.date().day)
    openP = row["Open"]
    highP = row["High"]
    lowP = row["Low"]
    closeP = row["Close"]
    expiryday = False
    
    newday = True
    newday = not(i > 0 and datentime.date().day != bnfResampled.loc[i-1,"Date"].day)
     ## If T = 9 20 open position at the money strike with the stop loss of 25% on each leg 
     ## if T = 15 10 close the remaining positions automatically
    
    if not isOptionsExpiryDay(datentime) : continue
        
    strike = str(round(round(closeP,-2)))
    
    if newday and datentime.time().hour == 9 and datentime.time().minute == 20 :
        
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
       
       
    # if newday and datentime.time().hour == 10 and datentime.time().minute == 20 : 
    #      #print(tickerSymbol.upper())
    #      #print("execute straddle")
    #      tickerSymbolCE = csv_database.getBnfOptionsTickerSymbol(datentime, strike, "CE")
    #      tickerSymbolPE = csv_database.getBnfOptionsTickerSymbol(datentime, strike, "PE")
         
    #      CE_df = csv_database.getTicker(datentime, tickerSymbolCE, tf_5Min)
    #      PE_df = csv_database.getTicker(datentime, tickerSymbolPE, tf_5Min)
         
    #      """ CE EXECUTION """
         
    #      startTime = onlyDate.replace(hour = 9, minute = 15)
    #      endTime = onlyDate.replace(hour = 10, minute = 15)
         
    #      ceSl = CE_df[startTime : endTime]["High"].max()
    #      ceSldf = CE_df[startTime : endTime]["High"]

    #      ce_entry = placeOrder(tickerSymbolCE, CE_df, datentime, ceSl, lotSize, "short", isSLper = False)
                 
    #      peSl = PE_df[startTime : endTime]["High"].max()
    #      """ PE EXECUTION """
    #      pe_entry = placeOrder(tickerSymbolPE, PE_df, datentime, peSl, lotSize, "short", isSLper = False)
         
    #      """ ADD OPEN POSITIONS TO THE POSITIONS LIST """
    #      positions[pe_entry.tradeId] = pe_entry
    #      positions[ce_entry.tradeId] = ce_entry
         
    #      priceTrackerDf[pe_entry.tradeId] = PE_df
    #      priceTrackerDf[ce_entry.tradeId] = CE_df
 
    #     # print(datentime.time())
       
        
    """ CLOSE THE ALL POSITIONS IF TIME IS 15:10 and ABOVE"""    
    if datentime.time().hour >= 15 and datentime.time().minute >= 10 and len(positions) != 0 :    
       # print("squared off positions")
        for tradeId in list(positions):
            trade = positions[tradeId]
            
            exitPrice = 0
            if trade.isOpen and trade.orderStatus == 1: 
                if (datentime in priceTrackerDf[tradeId].index):
                    exitPrice = priceTrackerDf[tradeId].loc(axis = 0)[datentime,"Close"]
                else :
                    print("No data available for this datetime so getting the last traded price for that day")
                    startTime = onlyDate.replace(hour = 9, minute = 15)
                    endTime = onlyDate.replace(hour = 15, minute = 25)
                    exitPrice = priceTrackerDf[tradeId].loc(axis = 0)[startTime : endTime, "Close"][-1]
                    
            trade.closePosition(datentime, "cover", exitPrice)
            positions.pop(tradeId)
            priceTrackerDf.pop(tradeId)
            tradeBook.addTrade(trade)
        #print(datentime.time())
        
    """ IF THE TIME IS 9:20 and ABOVE CHECK POSITIONS FOR STOPLOSS AND EXECUTE THE PENDING ORDER """    
    if datentime.time().hour >= 9 and datentime.time().minute > 20 :
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
                barHigh = priceTrackerDf[tradeId].loc(axis = 0)[datentime, "High"]
                
                if barHigh > slprice : 
                    exitPrice = slprice + slippage
                    trade.closePosition(datentime, "cover", exitPrice)
                    
                    
                    
                    positions.pop(tradeId)
                    priceTrackerDf.pop(tradeId)
                    
                    
                    
                    tradeBook.addTrade(trade)
      

#%%

tradeBook.addAllTradertoDf()
tradeBook.exportTradebookToCSV("920_expiryTrades_with_ORB.csv")

#%%
backtestedReportDf = tradeBook.tradeBookDf

cumSeries = pd.Series(bt.CumulativeCapital(backtestedReportDf["profit"].tolist(), 200000))
cumSeries.round()
cumSeries.plot()
        


    
    
    
    
 





















