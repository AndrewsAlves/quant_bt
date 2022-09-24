# -*- coding: utf-8 -*-
"""
Created on Fri Sep  21 4:55:20 2022

@author: andrewsalves

CSV database management for all backtesting and other analysis process

"""

import pandas as pd
import datetime as dt


path_bnfdb = "D:\\andyvoid\\data\\quotes\\csv_database\\banknifty"
path_bnfOptionsdb = "D:\\andyvoid\\data\\quotes\\csv_database\\banknifty\\options"
path_bnfIndicesdb = "D:\\andyvoid\\data\\quotes\\csv_database\\banknifty\\indices"
bnfTickerDf = None

#%% 

""" THIS CELL IS TO GET BANKNIFTY OPTIONS DATABASE """

def getBnfOptionsTickerDb() : 
    df = pd.read_csv(path_bnfOptionsdb + "\\" + "BNF_TICKER_DB_2017_2021.csv")
    df['Expiry Date'] = pd.to_datetime(df['Expiry Date'])
    return df


def getBnfOptionsTickerSymbol(datetime, strike, PEorCE) : 
    
    allTickerExpiries = getBnfOptionsTickerDb()
    
    onlyDate = dt.datetime(datetime.date().year, datetime.date().month, datetime.date().day)
    isExpiryday = onlyDate in allTickerExpiries["Expiry Date"].tolist()
    if isExpiryday :
        d = datetime.date().strftime("%d").zfill(2)
        upcomingExpiry = d + datetime.date().strftime("%b%y")             
    else :
        upcoming_expiries = allTickerExpiries["Expiry Date"] > datetime
        first_occ = upcoming_expiries.idxmax()
        upcomingExpiryDate =  allTickerExpiries.loc[first_occ, "Expiry Date"]
        d = upcomingExpiryDate.date().strftime("%d").zfill(2)
        upcomingExpiry = d + upcomingExpiryDate.date().strftime("%b%y")             
            
    tickerSymbol = "BANKNIFTY" + upcomingExpiry + strike + PEorCE
    
    return tickerSymbol.upper()

def getTicker(datetime, tickerSymbol, timeframe = "1Min") : 
    
    tickerDf = pd.read_csv(path_bnfOptionsdb + "\\" + str(datetime.date().year) + "\\" + tickerSymbol + ".csv")
    
    tickerDf['Date'] = pd.to_datetime(tickerDf['Date'])
    tickerDf = tickerDf.drop_duplicates(subset = ['Date'],keep = 'first')
    tickerDf.set_index('Date', inplace = True)
    
    reindexDate = pd.date_range(tickerDf.index[0], dt.datetime(tickerDf.index[-1].date().year, tickerDf.index[-1].date().month, tickerDf.index[-1].date().day, hour = 15, minute = 29), freq="1Min")
    tickerDf = tickerDf.reindex(reindexDate)
    
    tickerResampled = tickerDf.Close.resample(timeframe).ohlc().fillna(method = "ffill")
    tickerResampled["ticker"] = tickerSymbol.upper()
    
    return tickerResampled


#%%
""" THIS CELL IS TO GET BANKNIFTY INDICES DATABASE """

def get_banknifty_data(startDate, endDate, timeframe, local = True) : 
    if local == True:
        datadf = pd.read_csv(path_bnfIndicesdb + "\\" + "BANKNIFTY_2017_2021.csv", parse_dates=True)
        datadf['Date'] = pd.to_datetime(datadf['Date'])
        datadf.set_index('Date', inplace = True)
        bnf_resampled = datadf[startDate : endDate]['Close'].resample(timeframe).ohlc().dropna()
        bnf_resampled.reset_index(inplace = True)
        return bnf_resampled
    else:
        print("No API spcified")
        return







