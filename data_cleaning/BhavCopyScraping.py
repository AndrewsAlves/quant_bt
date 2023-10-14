# -*- coding: utf-8 -*-
import pandas as pd
import datetime as dt
from bhavcopy import bhavcopy
import os
#%%
gdflDf = pd.read_csv("G:\\andyvoid\\data\\quotes\\csv_database\\banknifty\\options\\2021\\BANKNIFTY07JAN2131200CE.csv")
df2 = pd.read_csv("G:\\andyvoid\\data\\quotes\\eodIeod\\2101\\banknifty\\BANKNIFTY21FEB26400CE.csv")
#%%
gdflDf = pd.read_csv("G:\\andyvoid\\data\\quotes\\csv_database\\bnf2011-16.csv")
gdflDf['duplicated'] = gdflDf['Date'].duplicated()

#%%
gdflNonDuplicate = gdflDf.drop_duplicates('Date', keep='first')
gdflNonDuplicate.drop('duplicated', axis=1, inplace=True)

gdflNonDuplicate.to_csv("G:\\andyvoid\\data\\quotes\\csv_database\\banknifty\\indices\\NIFTY_BANK_2011_2023_AUG.csv", index= False)

#%%
datastorage = "G:\\andyvoid\\bhav"
os.chdir(datastorage)
startDate = dt.date(2019,1,1)
endDate = dt.date(2019,12,31)
wait_time = [1, 2]
nse = bhavcopy("derivatives", startDate, endDate, datastorage, wait_time)
nse.get_data()

#%%
bhavcopyDf = pd.read_csv("G:\\andyvoid\\data\\quotes\\bhav\\derivatives2020.csv")
bhavgroupedDf = bhavcopyDf.groupby('SYMBOL')
niftyDerivatives = bhavgroupedDf.get_group('FINNIFTY')
niftyDerivatives.to_csv("G:\\andyvoid\\data\\quotes\\bhav\\finnifty\\finnifty_derivatives_2020.csv", index= False)
#%%
nifty = pd.read_csv("G:\\andyvoid\\data\\quotes\\bhav\\finnifty\\finnifty_derivatives_2022.csv")
nifty['EXPIRY_DT'] = pd.to_datetime(nifty['EXPIRY_DT'])
nifty['TIMESTAMP'] = pd.to_datetime(nifty['TIMESTAMP'])
nifty2 = nifty.loc[nifty['EXPIRY_DT'] == nifty['TIMESTAMP']]
nifty2.drop(['INSTRUMENT','OPEN','HIGH','LOW','CLOSE', 'SETTLE_PR','CONTRACTS','VAL_INLAKH','OPEN_INT','CHG_IN_OI'], axis=1, inplace=True)
nifty2.to_csv("G:\\andyvoid\\data\\quotes\\bhav\\finnifty\\finnifty_2022_CEPE_AllStrikes.csv", index= False)
#%% 

""" ADD YEAR STRIKES AND EXPIRY DATE TO ALL STIRKE AND EXPIRIES DATABASE """
allStrikesExpiry = pd.read_csv("G:\\andyvoid\\data\\quotes\\csv_database\\FINNIFTY\\options\\option_symbols.csv")
allStrikesDf = pd.read_csv("G:\\andyvoid\\data\\quotes\\bhav\\finnifty\\finnifty_2023_CEPE_AllStrikes.csv")
allStrikesDf['expiry'] = pd.to_datetime(allStrikesDf['EXPIRY_DT'])
allStrikesDf = allStrikesDf[allStrikesDf['STRIKE_PR'] != 0]
allStrikesDf['Ticker'] = (allStrikesDf['SYMBOL'] + allStrikesDf['expiry'].dt.strftime("%d%b%y") + allStrikesDf['STRIKE_PR'].astype(int).astype(str) + allStrikesDf['OPTION_TYP']).str.upper()
allStrikesDf['Expiry Date'] = allStrikesDf['EXPIRY_DT']
allStrikesDf.drop(['SYMBOL','EXPIRY_DT','STRIKE_PR', 'OPTION_TYP', 'TIMESTAMP', 'expiry'], axis=1, inplace=True)
allStrikesDf = allStrikesDf[['Ticker','Expiry Date']]
allStrikesExpiry = allStrikesExpiry.append(allStrikesDf)
allStrikesExpiry.sort_values(by='Expiry Date', inplace=True)
#%%
allStrikesExpiry.to_csv("G:\\andyvoid\\data\\quotes\\csv_database\\FINNIFTY\\options\\option_symbols.csv", index= False)






