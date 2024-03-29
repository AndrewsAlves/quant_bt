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
opdf['Date'] = pd.to_datetime(opdf["Date"], format = "%d/%m/%Y-%H:%M") ##errors = 'coerce')
#naT = opdf[opdf['Date2'].isnull()]
opdf.drop(['Time'], inplace = True, axis = 1)

#opdf.columns = opdf.columns.str.replace(' ', '')
#opdf.rename(columns = {'Openinterest':'OpenInterest'}, inplace = True)
#tickerDatabase = opdf["Ticker"].drop_duplicates(keep = 'first').to_frame()
#isOptions = tickerDatabase["Ticker"].str.len() < 20
#tickerDatabase.drop(isOptions[isOptions].index, inplace = True)
#tickerDatabase["Expiry Date"] = tickerDatabase["Ticker"].str.replace("NIFTY","").map(lambda x: str(x)[:7])
#tickerDatabase["Expiry Date"] = pd.to_datetime(tickerDatabase["Expiry Date"], format = "%d%b%y")
#tickerDatabase.sort_values(by=["Expiry Date"], inplace = True)
#tickerDatabase.reset_index(drop = True, inplace = True)

groupedOpdf = opdf.groupby("Ticker")
group_names = list(groupedOpdf.groups.keys())

for ticker in tqdm(group_names):
    tickerDf = groupedOpdf.get_group(ticker)
    tickerDf.to_csv("G:\\andyvoid\\data\\quotes\\csv_database\\nifty\\options\\2021\\" + ticker + '.csv', index = False)
    
#%%
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
#### CLEANING THE CSV GUY FILES
finniftyFiles = os.listdir('G:\\andyvoid\\data\\quotes\\csv guy\\Finnifty')

for file in tqdm(finniftyFiles, desc="Reading Options data") :
    df = pd.read_csv('G:\\andyvoid\\data\\quotes\\csv guy\\Finnifty\\' + file)
    df['Ticker'] = df['<ticker>']
    df["Date"] = df["<date>"].astype(str) + '-' + df["<time>"].astype(str)
    df['Date'] = pd.to_datetime(df["Date"], format = "%m/%d/%Y-%H:%M:%S")
    df['Open'] = df['<open>']
    df['High'] = df['<high>']
    df['Low'] = df['<low>']
    df['Close'] = df['<close>']
    df['Volume'] = df['<volume>']
    df['OpenInterest'] = df['<o/i> ']
    df.drop(['<ticker>','<date>','<time>','<open>','<high>','<low>','<close>','<volume>','<o/i> '], inplace = True, axis = 1)
    df.to_csv("G:\\andyvoid\\data\\quotes\\csv guy\\changed\\" + file, index = False)
    
#%%
finniftyFiles = os.listdir('G:\\andyvoid\\data\\quotes\\csv guy\\changed')

for file in tqdm(finniftyFiles, desc="Reading Options data") :
    
    strike = file[14:-4:1]
    expiryDate = file[8:-11:1]
    print(expiryDate)
    expiryDate = dt.datetime.strptime(expiryDate, '%y%m%d')
    expiryDate = expiryDate.strftime('%d%b%y')
    ticker= 'FINNIFTY' + expiryDate + strike
    print(ticker)

    df = pd.read_csv('G:\\andyvoid\\data\\quotes\\csv guy\\Finnifty\\' + file)
    df['<ticker>'] = ticker.upper()
    df['Ticker'] = df['<ticker>']
    df["Date"] = df["<date>"].astype(str) + '-' + df["<time>"].astype(str)
    df['Date'] = pd.to_datetime(df["Date"], format = "%m/%d/%Y-%H:%M:%S")
    df['Open'] = df['<open>']
    df['High'] = df['<high>']
    df['Low'] = df['<low>']
    df['Close'] = df['<close>']
    df['Volume'] = df['<volume>']
    df['OpenInterest'] = df['<o/i> ']
    df.drop(['<ticker>','<date>','<time>','<open>','<high>','<low>','<close>','<volume>','<o/i> '], inplace = True, axis = 1)
    df.to_csv("G:\\andyvoid\\data\\quotes\\csv guy\\changed2\\" + ticker.upper() + '.csv', index = False)







