
"""
Created on Wed Aug 22 15:15:17 2022

###########################################
### 920 STRADLE BACKTESTING BNF  ##########
###########################################

@author: AndyAlves
"""
#%%
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import datetime as dt
from tqdm import tqdm
import math
from backtesting import Backtesting as bt
import traceback
import logging
from backtesting import LocalCsvDatabase
from backtesting.LocalCsvDatabase import CsvDatabase
from backtesting import Backtesting
from backtesting import StrategyArsenal as sa
import Utils
#%%
# Variables
tf_1Min = "1Min"
tf_5Min = "5Min"
tf_15Min = "15Min"
tf_1H = "H"
tf_1D = "1D"
strTimeformat = "%Y/%m/%d - %H:%M:%S"

#start_date = '2017-01'
#end_date = '2023-08'
start_date = '2022-1'
end_date = '2023-08'
O = "Open"
H = "High"
L = "Low"
C = "Close"

hour = 11
minute = 15

#%%
csvDatabase = CsvDatabase(LocalCsvDatabase.FINNIFTY)
bnfResampled = csvDatabase.getSymbolTimeSeries(start_date, end_date, tf_5Min)

#%%

"""
920 strategy and backtesting section 
Time frame = 5m 
"""

tradeBook = bt.TradeBook()
positions = {}
priceTrackerDf = {}
SLper = 25
lotSize = 40
strikeDiff = 100
slippage = 1
qty = 50
riskPerTrade = 1 # percentage of capital%
capital = 1000000
marginPerLot = 110000
circular4402 = dt.datetime(2022,10,18)

dfTemp = pd.DataFrame()

def addMissingData(ticker, dataType):
    dic = {"ticker" : ticker, "data_type" : dataType}
    tradeBook.missingData = tradeBook.missingData.append(dic, ignore_index= True)
    
def placeOrder(tickerSymbol, tickerDf, datetime, SLper, qty, tradeType, tradeObj = None, adaptivePs = False) :
    if tradeObj == None : 
        tradeObj = bt.Trade()
        tradeObj.tradeId = id(tradeObj)
        
    entryprice = 0
    sl = 0
    orderStatus = 0
    
    if tickerDf is None:
        print("\n Order execution pending, Dataframe None: " + tickerSymbol + " " , datetime)
    else :
        if datetime in tickerDf.index :
            entryprice = tickerDf.loc(axis = 0)[datetime, "Open"]
            sl = entryprice + (entryprice / 100) * SLper
            if adaptivePs : 
                qty = Utils.getPositionsSizingForSelling(abs(sl - entryprice), ((capital / 100) * riskPerTrade),
                                                         lotSize,
                                                         marginPerLot,
                                                         capital,
                                                         False)
            orderStatus = 1
        else :
            addMissingData(tickerSymbol, datetime.strftime(strTimeformat))
            #missingData.append(tickerSymbol + " " + datetime.strftime(strTimeformat))
            print("\n Order execution pending, price data not found : " + tickerSymbol + " " , datetime)
    
    tradeObj.openPosition(tickerSymbol, datetime, tradeType, qty, entryprice, SLprice = sl, isOptions = True, orderStatus = orderStatus)
    return tradeObj

def getOptionDfAdjusted(strike, datetime) :
    symbolCe, ceDf = getOptionsDf(datetime, strike, "CE")
    symbolPe, peDf = getOptionsDf(datetime, strike, "PE")
    ceLTP = 0
    peLTP = 0
    
    if ceDf is not None :
        try: 
            ceLTP =  Utils.getPriceDataFromDataframe(ceDf, datetime, "Close")
        except : 
            addMissingData(symbolCe, datetime.strftime(strTimeformat))
            print("\n Error at Strike Selection price data not found : " + symbolCe + " " + symbolPe + " " , datetime)
            return symbolCe, ceDf, symbolPe, peDf
    
    if peDf is not None :
        try: 
            peLTP =  Utils.getPriceDataFromDataframe(peDf, datetime, "Close")
        except : 
            addMissingData(symbolPe, datetime.strftime(strTimeformat))
            print("\n Error at Strike Selection price data not found : " + symbolCe + " " + symbolPe + " " , datetime)
            return symbolCe, ceDf, symbolPe, peDf

    diff = abs(ceLTP - peLTP)
    
    #find nearest ITM Strike 
    if ceLTP > peLTP :
        SymbolPeNew, peDfNew = getOptionsDf(datetime, str(int(strike) + strikeDiff), "PE")
        
        if peDfNew is not None :
            try :
                peDfNewLTP =  Utils.getPriceDataFromDataframe(peDfNew, datetime, "Close")
            except :
                addMissingData(SymbolPeNew, datetime.strftime(strTimeformat))
                print("\n Error at Strike Selection price data not found : " + symbolCe + " " + SymbolPeNew + " " , datetime)
                return symbolCe, ceDf, symbolPe, peDf
            
            newDiff = abs(ceLTP - peDfNewLTP)
            if newDiff < diff : 
                #print('CE - ' + symbolCe + "New PE - " + SymbolPeNew)
                return symbolCe, ceDf, SymbolPeNew, peDfNew
    else : 
        SymbolCeNew, ceDfNew = getOptionsDf(datetime, str(int(strike) - strikeDiff), "CE")
        
        if ceDfNew is not None :
            try :
                ceDfNewLTP =  Utils.getPriceDataFromDataframe(ceDfNew, datetime, "Close")
            except :
                addMissingData(SymbolCeNew, datetime.strftime(strTimeformat))
                print("Error at Strike Selection price data not found : " + SymbolCeNew + " " + symbolPe + " " , datetime)
                return symbolCe, ceDf, symbolPe, peDf
            
            newDiff = abs(ceDfNewLTP - peLTP)
            if newDiff < diff : 
                #print('New CE - ' + SymbolCeNew + "PE - " + symbolPe)
                return SymbolCeNew, ceDfNew , symbolPe, peDf
        
    return symbolCe, ceDf, symbolPe, peDf

def getOptionsDf(datetime, strike, CEorPE) :
    tickerSymbol = csvDatabase.getOptionsTickerSymbol(datetime, strike, CEorPE)
    df = csvDatabase.getOptionsSymbolTimeSeries(datetime, tickerSymbol, tf_5Min)
    if df.empty :
        df = None
        addMissingData(tickerSymbol, "Dataframe Empty")
    return tickerSymbol, df

def getstrikeFromLtp(ltp) :
    return strikeDiff * round(ltp // strikeDiff)

for i, row in tqdm(bnfResampled.iterrows(), desc = "Backtesting", total = bnfResampled.shape[0]): 
    
    datentime = row["Date"]
    onlyDate = dt.datetime(datentime.date().year, datentime.date().month, datentime.date().day)
    openP = row["Open"]
    highP = row["High"]
    lowP = row["Low"]
    closeP = row["Close"]
    expiryday = False
    
    if datentime >= circular4402 : 
        print("Changed strike interval")
        strikeDiff = 50
    
    if i > 0 and datentime.date().day != bnfResampled.loc[i-1,"Date"].day: newday = True
    else : newday = False
    
    if i == 0 : newday = True
     ## If T = 9 20 open position at the money strike with the stop loss of 25% on each leg 
     ## if T = 15 10 close the remaining positions automatically
    
    #strike = str(round(round(closeP,-2)))
    strike = str(getstrikeFromLtp(closeP))
    #print(closeP)
    #print(strike)
    
    if datentime.time().hour == hour and datentime.time().minute == minute :
        
        #print(tickerSymbol.upper())
        #print("execute straddle")
        
        tickerSymbolCE, CE_df, tickerSymbolPE, PE_df = getOptionDfAdjusted(strike, datentime)

        """ CE EXECUTION """
        ce_entry = placeOrder(tickerSymbolCE, CE_df, datentime, SLper, qty, "short", adaptivePs = True)
                
        """ PE EXECUTION """
        pe_entry = placeOrder(tickerSymbolPE, PE_df, datentime, SLper, ce_entry.qty, "short", adaptivePs=False)
        
        """ ADD OPEN POSITIONS TO THE POSITIONS LIST """
        positions[pe_entry.tradeId] = pe_entry
        positions[ce_entry.tradeId] = ce_entry
        
        priceTrackerDf[pe_entry.tradeId] = PE_df
        priceTrackerDf[ce_entry.tradeId] = CE_df

       # print(datentime.time())
        
    """ IF THE TIME IS 9:20 and ABOVE CHECK POSITIONS FOR STOPLOSS AND EXECUTE THE PENDING ORDER """  
    datentimeCheck = datentime.replace(hour=9, minute=15)
    if datentime >= datentimeCheck :
        for tradeId in list(positions) :
            trade = positions[tradeId]
            
            """ Check order status and execute the pending order"""
            if trade.orderStatus == 0 and tradeId in priceTrackerDf : 
                placeOrder(trade.symbol, priceTrackerDf[tradeId], datentime, SLper, qty, "short", tradeObj = trade, adaptivePs= True)
                                
            """ Check order status and track the SL price"""
            if trade.orderStatus == 1 and tradeId in priceTrackerDf : 
                
                
                if not(datentime in priceTrackerDf[tradeId].index):
                    print("Datatime not present")
                    continue
                    
                slprice = trade.stopLossPrice
                barHigh = priceTrackerDf[tradeId].loc(axis = 0)[datentime, "High"]
                
                if barHigh > slprice : 
                    exitPrice = slprice + slippage
                    trade.closePosition(datentime, "cover", exitPrice)
                    
                    positions.pop(tradeId)
                    priceTrackerDf.pop(tradeId)
                    
                    tradeBook.addTrade(trade)
                    
                    
    """ CLOSE THE ALL POSITIONS IF TIME IS 15:10 and ABOVE"""    
    datentimeCheck = datentime.replace(hour=15, minute=10)
    if datentime >= datentimeCheck and len(positions) != 0 :    
       # print("squared off positions")
        for tradeId in list(positions):
            trade = positions[tradeId]
            
            exitPrice = 0
            if trade.isOpen and trade.orderStatus == 1: 
                if (datentime in priceTrackerDf[tradeId].index):
                    exitPrice = priceTrackerDf[tradeId].loc(axis = 0)[datentime,"Close"]
                else :
                    print("No data available for this datetime so getting the last traded price for that day")
                    exitPrice = 0

            trade.closePosition(datentime, "cover", exitPrice)
            positions.pop(tradeId)
            priceTrackerDf.pop(tradeId)
            tradeBook.addTrade(trade)
        #print(datentime.time())
      

#%%
#daysList = ['Monday', 'Tuesday']
tradesDf, report, dailyReturn = tradeBook.generateReport("FINNIFTY","finnifty 9 20 25SL classic", capital , ['Monday', 'Tuesday'])

#%%

strategyAr = sa.StrategyArsenal()

flag = {}
flag['id'] = strategyAr.getNewStrategyId()
flag['strategy_name'] = "Finnifty 11 15 25 SL Classic"
flag['start_date'] = start_date
flag['end_date'] = end_date
flag['desc'] = "11 15 am short straddle with 25% stoploss based on premium and Lot size based on adaptive position sizing based on points and Max size is based on capital"
flag['stars'] = 3

#%%
stgId, strategies = strategyAr.addStrategy(flag, tradeBook)

#%%


        


    
    
    
    
 






















