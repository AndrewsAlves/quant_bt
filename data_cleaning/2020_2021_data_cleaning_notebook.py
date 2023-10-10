# -*- coding: utf-8 -*-
"""
Created on Tue Sep 13 14:49:38 2022

CLEANING 2020 and 2021 data

@author: Admin
"""

import pandas as pd 
import datetime as dt
import os, os.path
from tqdm import tqdm
import  numpy as np

#%% 
""" THIS SECTION IS TO CLEAN BANKNIFTY OLD DATA """

#Get banknifty and store it in Dataframe
# bnf_data = get_banknifty_data(True)
# bnf_data["Date"] = bnf_data["Date"].replace(to_replace= '/', value= '', regex=True)
# bnf_data["Date"] = bnf_data["Date"].astype(str) + '-' + bnf_data["Time"].astype(str)
# bnf_data['Date'] = pd.to_datetime(bnf_data["Date"] , format = "%Y%m%d-%H:%M")
# bnf_data.drop(['Time'], inplace = True, axis = 1)
# bnf_data.set_index('Date', inplace = True)
# bnf_resample = bnf_data[start_date : end_date][C].resample(m5).ohlc().dropna()
# bnf_resample.reset_index(inplace = True)

#%%

bnf_op_path = "G:\\andyvoid\\data\\quotes\\Archives\\After_cleaned\\Nifty\\options"

def getOptionsData(year) :
    month_fol = os.listdir(bnf_op_path + "\\" + year)
    opdf = pd.DataFrame()
    ##Reading options data and using a tqdm Progress bar 
    for month in month_fol : 
       fnofiles = os.listdir(bnf_op_path + "\\" + year + "\\" + month)
       for file in tqdm(fnofiles, desc="Reading Options data - " + month + " " + year):
           df = pd.read_csv(bnf_op_path + "\\" + year + "\\" + month + "\\" + file)
           opdf = opdf.append(df)
           #print(opdf)
    return opdf    

rawOpdf = pd.DataFrame()
years_fols = ['2021'] ##['2017','2018','2019','2020','2021']
for year in years_fols: 
    
    if year == "2016" : 
        continue
    
    rawOpdf = rawOpdf.append(getOptionsData(year))
    
#%%
##---------------------------------------------------------------##
## COPY OPTIONS DATA AND PROCESS THEM FOR BACKTESTING
opdf = rawOpdf.copy(deep = True)

#%%

opdf["Date"] = opdf["Date"].astype(str) + '-' + opdf["Time"].astype(str).map(lambda x: str(x)[:-3])
print(opdf.head())
opdfError = opdf[opdf['Date'] == '12-01-2021-09:49']
opdf.at[23661, 'Date'] = '20/07/2020-13:27'
opdf.at[61424, 'Date'] = '20/07/2020-13:05'
opdf.at[61597, 'Date'] = '20/07/2020-14:55'

## 61597-- 20/07/2020-  14:55, 61424-- 20/07/2020-  13:05, 

opdf['Date'] = pd.to_datetime(opdf["Date"], format = "%d/%m/%Y-%H:%M") ##errors = 'coerce')
print(opdf.tail())

#naT = opdf[opdf['Date2'].isnull()]
opdf.drop(['Time'], inplace = True, axis = 1)

#opdf.columns = opdf.columns.str.replace(' ', '')
#opdf.rename(columns = {'Openinterest':'OpenInterest'}, inplace = True)
#11300CE
# opdfNew = pd.DataFrame()
# opdfNew['Ticker'] = opdf['Ticker']
# opdfNew['Date'] = opdf['Date']
# opdfNew['Open'] = opdf[['Open', 'Open']].max(axis=1)
# opdfNew['High'] = opdf[['High', 'High']].max(axis=1)
# opdfNew['Low'] = opdf[['Low', 'Low']].max(axis=1)
# opdfNew['Close'] = opdf[['Close', 'Close']].max(axis=1)
# opdfNew['Volume'] = opdf[['Volume', 'Volume']].max(axis=1)
opdf['Open Interest2'] = opdf[['Open Interest','Open Inerest', 'OpenInterest', 'Open interest']].max(axis=1)
#opdf['Open Interest'] = opdf['Open Interest2']
opdf.drop(['Open Interest','Open Inerest', 'OpenInterest', 'Open interest'], inplace = True, axis = 1)
opdf['Open Interest'] = opdf['Open Interest2']
opdf.drop(['Open Interest2'], inplace = True, axis = 1)


#tickerDatabase = opdf["Ticker"].drop_duplicates(keep = 'first').to_frame()
#isOptions = tickerDatabase["Ticker"].str.len() < 20
#tickerDatabase.drop(isOptions[isOptions].index, inplace = True)
#tickerDatabase["Expiry Date"] = tickerDatabase["Ticker"].str.replace("NIFTY","").map(lambda x: str(x)[:7])
#tickerDatabase["Expiry Date"] = pd.to_datetime(tickerDatabase["Expiry Date"], format = "%d%b%y")
#tickerDatabase.sort_values(by=["Expiry Date"], inplace = True)
#tickerDatabase.reset_index(drop = True, inplace = True)

groupedOpdf = opdf.groupby("Ticker")
group_names = list(groupedOpdf.groups.keys())

#%%
for ticker in tqdm(group_names):
    tickerDf = groupedOpdf.get_group(ticker)
    tickerDf.to_csv("G:\\andyvoid\\data\\quotes\\csv_database\\nifty\\options\\2021\\" + ticker + '.csv', index = False)





#%%
#13-01-2021
#14-01-2021
#15-01-2021
#18-01-2021
#19-01-2021
#20-01-2021
#22-01-2021
#28-01-2021
#29-01-2021

#01-02-2021
#02-02-2021
#03-02-2021
#05-02-2021
#09-02-2021
#10-02-2021
#11-02-2021
#15-02-2021
#17-02-2021
#18-02-2021
#23-02-2021
#25-02-2021
#26-02-2021

#01-03-2021
#02-02-2021
#01-02-2021

#25-06-2021


""" THIS SECTION CLEANES THE SPECIFIED FILES FOR TGE RIGHT DATE TIME STRING FORMAT """
mm_dd_df = pd.read_csv("G:\\andyvoid\\data\\quotes\\Archives\\After_cleaned\\Nifty\\options\\2021\\10\\NIFTY_NFO_BACKADJUSTED_12102021.csv")
mm_dd_df["Date"] = pd.to_datetime(mm_dd_df["Date"], format= "%d-%m-%Y")
mm_dd_df["Date"] = mm_dd_df["Date"].dt.strftime("%d/%m/%Y")
mm_dd_df.to_csv("G:\\andyvoid\\data\\quotes\\Archives\\After_cleaned\\Nifty\\options\\2021\\10\\NIFTY_NFO_BACKADJUSTED_12102021.csv", index= False)

#%%
""" THIS SECTION CLEANES THE SPECIFIES FILES IN 2021"""

mm_dd_df = pd.read_csv("D:\\andyvoid\data\quotes\After_cleaned\Banknifty\BNF_options\\2020\\08\\BANKNIFTY_NFO_25082020.csv")
mm_dd_df["Date"] = pd.to_datetime(mm_dd_df["Date"], format = "%d-%m-%Y")
mm_dd_df["Date"] = mm_dd_df["Date"].dt.strftime("%d/%m/%Y")
mm_dd_df.to_csv("D:\\andyvoid\data\quotes\After_cleaned\Banknifty\BNF_options\\2020\\08\\BANKNIFTY_NFO_25082020_changeed.csv", index= False)

#%%

""" THIS SECTION CLEANES THE .NFO STRING FROM THE TICKER STRING """

bnf_op_path = "G:\\andyvoid\\data\\quotes\\Archives\\After_cleaned\\Nifty\\options"

#df = pd.read_csv(bnf_op_path + "\\" + "2021" + "\\" + "01" + "\\" + "BANKNIFTY_NFO_BACKADJUSTED_04012021.csv", parse_dates=True)
#df["Ticker"] = df["Ticker"].str.replace(".NFO", "")


def getOptionsData(year) :
    month_fol = os.listdir(bnf_op_path + "\\" + year)
    opdf = pd.DataFrame()
    ##Reading options data and using a tqdm Progress bar 
    for month in month_fol : 
       fnofiles = os.listdir(bnf_op_path + "\\" + year + "\\" + month)
       for file in tqdm(fnofiles, desc="Reading Options data - " + month + " " + year):
           df = pd.read_csv(bnf_op_path + "\\" + year + "\\" + month + "\\" + file)
           df["Ticker"] = df["Ticker"].str.replace(".NFO", "")
           df.to_csv(bnf_op_path + "\\" + year + "_changed" + "\\" + month + "\\" + file, index = False)
           #print(opdf)
    return opdf    

getOptionsData("2021")

#%%
bnfRaw = pd.read_csv("G:\\andyvoid\\data\\quotes\\csv_database\\banknifty\\indices\\BNF_2010_2020.csv")
bnfRaw["Date"] = bnfRaw["Date"].astype(str) + '-' + bnfRaw["Time"].astype(str)
bnfRaw['Date'] = pd.to_datetime(bnfRaw["Date"], format = "%Y%m%d-%H:%M") ##errors = 'coerce')
#naT = opdf[opdf['Date2'].isnull()]
bnfRaw.drop(['Time'], inplace = True, axis = 1)
bnfRaw.to_csv("G:\\andyvoid\\data\\quotes\\csv_database\\banknifty\\indices\\BNF_2010_2020_cleaned.csv", index= False)

#%%
vixRaw = pd.read_csv("G:\\andyvoid\\data\\quotes\\csv_database\\india_vix\\INDIA_VIX_2010_2023.csv")
vixRaw['Date'] = vixRaw['Date'].astype(str).map(lambda x: str(x)[4:-31])
vixRaw['Date'] = pd.to_datetime(vixRaw["Date"], format = "%b %d %Y %H:%M:%S")
vixRaw.to_csv("G:\\andyvoid\\data\\quotes\\csv_database\\india_vix\\INDIA_VIX_2010_2023_cleaned.csv", index= False)

#%%








