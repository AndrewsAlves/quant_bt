
"""
Created on Wed Aug 22 15:15:17 2022

###########################################
### 920 STRADLE BACKTESTING BNF  ##########
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

# Variables
m1 = "1Min"
m5 = "5Min"
m15 = "15Min"
h = "H"
d = "1D"

start_date = '2019-01'
end_date = '2019-12'
O = "Open"
H = "High"
L = "Low"
C = "Close"
bnf_op_path = "D:\DSW\Datas\quotes\After_cleaned\Banknifty\BNF_options"

#%%
def get_banknifty_data(local = True) : 
    if local == True:
        data = pd.read_csv("D:\DSW\Datas\quotes\After_cleaned\Banknifty\BNF_INDICES\BNF_2017_2021.csv", parse_dates=True)
        data.drop(['useless1','useless2'], axis=1, inplace = True)
        return data
    else:
        print("No API spcified")
        return
#%%
def getOptionsData(year) :
    month_fol = os.listdir(bnf_op_path + "\\" + year)
    opdf = pd.DataFrame()
    ##Reading options data and using a tqdm Progress bar 
    for month in month_fol : 
       fnofiles = os.listdir(bnf_op_path + "\\" + year + "\\" + month)
       for file in tqdm(fnofiles, desc="Reading Options data - " + month + " " + year):
           df = pd.read_csv(bnf_op_path + "\\" + year + "\\" + month + "\\" + file, parse_dates=True)
           opdf = opdf.append(df)
           #print(opdf)
    return opdf    

#%%
##GET TICKER FUNCTION to get specified option ticker and its values
def getTicker(ticker, timeframe) :
    tickerDf = groupedOpdf.get_group(ticker.upper())
    tickerDf = tickerDf.drop_duplicates(subset = ['Date'],keep = 'first')
    tickerDf.set_index('Date', inplace = True)
    
    reindexDate = pd.date_range(tickerDf.index[0], dt.datetime(tickerDf.index[-1].date().year, tickerDf.index[-1].date().month, tickerDf.index[-1].date().day, hour = 15, minute = 29), freq="1Min")
    tickerDf = tickerDf.reindex(reindexDate)
    
    tickerResampled = tickerDf.Close.resample(timeframe).ohlc().fillna(method = "ffill")
    tickerResampled["ticker"] = ticker.upper()
    return tickerResampled

#df_temp = getTicker("BANKNIFTY16NOV1725300PE", m5)

#%%

#Get banknifty and store it in Dataframe
bnf_data = get_banknifty_data(True)
bnf_data["Date"] = bnf_data["Date"].replace(to_replace= '/', value= '', regex=True)
bnf_data["Date"] = bnf_data["Date"].astype(str) + '-' + bnf_data["Time"].astype(str)
bnf_data['Date'] = pd.to_datetime(bnf_data["Date"] , format = "%Y%m%d-%H:%M")
bnf_data.drop(['Time'], inplace = True, axis = 1)
bnf_data.set_index('Date', inplace = True)

bnf_resample = bnf_data[start_date : end_date][C].resample(m5).ohlc().dropna()
bnf_resample.reset_index(inplace = True)

#%%

## GET OPTIONS DATA BY YEAR AND STORE IT IN A DATAFRAME
rawOpdf = pd.DataFrame()
years_fols = ['2019'] ##['2017','2018','2019','2020','2021']
for year in years_fols: 
    
    if year == "2016" : 
        continue
    
    rawOpdf = rawOpdf.append(getOptionsData(year))
    
##%%
##---------------------------------------------------------------##
## COPY OPTIONS DATA AND PROCESS THEM FOR BACKTESTING
opdf = rawOpdf.copy(deep = True)

opdf["Date"] = opdf["Date"].astype(str) + '-' + opdf["Time"].astype(str).map(lambda x: str(x)[:-3])
opdf['Date'] = pd.to_datetime(opdf["Date"], format = "%d/%m/%Y-%H:%M")
opdf.drop(['Time'], inplace = True, axis = 1)

tickerDatabase = opdf["Ticker"].drop_duplicates(keep = 'first').to_frame()
isOptions = tickerDatabase["Ticker"].str.len() < 20
tickerDatabase.drop(isOptions[isOptions].index, inplace = True)
tickerDatabase["Expiry Date"] = tickerDatabase["Ticker"].str.replace("BANKNIFTY","").map(lambda x: str(x)[:7])
tickerDatabase["Expiry Date"] = pd.to_datetime(tickerDatabase["Expiry Date"], format = "%d%b%y")
tickerDatabase.sort_values(by=["Expiry Date"], inplace = True)
tickerDatabase.reset_index(drop = True, inplace = True)

groupedOpdf = opdf.groupby("Ticker")

#%%

""" 
920 strategy and backtesting section 
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
        entryprice = tickerDf.loc(axis = 0)[datetime, "close"]
        sl = entryprice + (entryprice / 100) * SLper
        orderStatus = 1
    else :
        print("Order execution pending, price data not found")
    
    tradeObj.openPosition(tickerSymbol, datetime, tradeType, lotSize, entryprice, SLprice = sl, isOptions = True, orderStatus = orderStatus)
    return tradeObj
    

positions = pd.DataFrame(columns = {"Datetime", "instrument", "buy_price", "sell_price", "short_price", "cover_price", "p/l"})
upcomingEx = []
tradeBook = bt.TradeBook()
positions = {}
priceTrackerDf = {}
SLper = 25
lotSize = 25
slippage = 1

for i, row in tqdm(bnf_resample.iterrows(), desc = "Backtesting", total= bnf_resample.shape[0]): 
       
    datentime = row["Date"]
    openP = row["open"]
    highP = row["high"]
    lowP = row["low"]
    closeP = row["close"]
    expiryday = False
    
    newday = True
    newday = not(i > 0 and datentime.date().day != bnf_resample.loc[i-1,"Date"].day)
     ## If T = 9 20 open position at the money strike with the stop loss of 25% on each leg 
     ## if T = 15 10 close the remaining positions automatically
     
    if newday :
        onlyDate = dt.datetime(datentime.date().year, datentime.date().month, datentime.date().day)
        isExpiryday = onlyDate in tickerDatabase["Expiry Date"].tolist()
        if isExpiryday :
            d = datentime.date().strftime("%d").zfill(2)
            upcomingExpiry = d + datentime.date().strftime("%b%y")             
        else :
            upcoming_expiries = tickerDatabase["Expiry Date"] > datentime
            first_occ = upcoming_expiries.idxmax()
            upcomingExpiryDate =  tickerDatabase.loc[first_occ, "Expiry Date"]
            d = upcomingExpiryDate.date().strftime("%d").zfill(2)
            upcomingExpiry = d + upcomingExpiryDate.date().strftime("%b%y")             

    upcomingEx.append(upcomingExpiry)    
    tickerSymbol = "BANKNIFTY" + upcomingExpiry + str(round(round(closeP,-2)))
    
     
    if newday and datentime.time().hour == 9 and datentime.time().minute == 20 :
        
        #print("execute straddle")
        CE_df = getTicker(tickerSymbol + "CE", m5)
        PE_df = getTicker(tickerSymbol + "PE", m5)
        
        """ CE EXECUTION """
        ce_entry = placeOrder(tickerSymbol + "CE", CE_df, datentime, SLper, lotSize, "short")
                
        """ PE EXECUTION """
        pe_entry = placeOrder(tickerSymbol + "PE", PE_df, datentime, SLper, lotSize, "short")
        
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
            
            if trade.isOpen and trade.orderStatus == 1: 
                if (datentime in priceTrackerDf[tradeId].index):
                    exitPrice = priceTrackerDf[tradeId].loc(axis = 0)[datentime,"close"]
                else :
                    print("No data available for this datetime so getting the last traded price for that day")
                    startTime = onlyDate.replace(hour = 9, minute = 15)
                    endTime = onlyDate.replace(hour = 15, minute = 25)
                    exitPrice = priceTrackerDf[tradeId].loc(axis = 0)[startTime : endTime, "close"][-1]

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
                barHigh = priceTrackerDf[tradeId].loc(axis = 0)[datentime, "high"]
                
                if barHigh > slprice : 
                    exitPrice = slprice + slippage
                    trade.closePosition(datentime, "cover", exitPrice)
                    
                    positions.pop(tradeId)
                    priceTrackerDf.pop(tradeId)
                    
                    tradeBook.addTrade(trade)
       
        
        
#%%
tradeBook.addAllTradertoDf()

backtestedReportDf = tradeBook.tradeDf

cumSeries = pd.Series(bt.Cumulative(backtestedReportDf["profit"].tolist()))
cumSeries.plot()        
        


    
    
    
    























