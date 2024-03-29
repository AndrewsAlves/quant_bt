# -*- coding: utf-8 -*-
""" GETTING HISTORICAL DATA """
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd 
from datetime import datetime
from datetime import timedelta
from breeze_connect import BreezeConnect
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import webbrowser
import urllib
from tqdm import tqdm
import time
from ast import literal_eval
import os

#%%
APIKEY = "t34&7X948S606Z71P450eh6494517mXF"
APISECREAT = "%97050082x4`R612K27S(96U890+1866"

# Initialize SDK
breeze = BreezeConnect(api_key= APIKEY)
webbrowser.open_new("https://api.icicidirect.com/apiuser/login?api_key="+urllib.parse.quote_plus(APIKEY))

# Obtain your session key from https://api.icicidirect.com/apiuser/login?api_key=YOUR_API_KEY
# Incase your api-key has special characters(like +,=,!) then encode the api key before using in the url as shown below.
#print("https://api.icicidirect.com/apiuser/login?api_key="+urllib.parse.quote_plus(APIKEY))

# Generate Session
#%%
sessionCode = 35763194
result = breeze.generate_session(api_secret=APISECREAT,session_token=sessionCode)
print(result)

#%%
""" THIS SECTION IS TO RETRIVE SINGLE INDEX CASH / EQUITY DATA """

#FINNIFY - NIFFIN
#NIFTY - NIFTY
#BANKNIFTY - CNXBAN
#Ticker or Instrument ,Date,Open,High,Low,Close,Volume,Open Interest
startDate  = datetime(2023, 11, 18, 9, 0, 0)
endDate  = datetime(2023, 11, 19, 15, 35, 0)
instrument = "NIFFIN"
segment = ["cash","options"]
priceDf = pd.DataFrame()
exchage_code = ["NSE","NFO"]
option = ['call', 'put']
stopDate = datetime(2024, 2, 26)

days = range(2333)
for i in tqdm(days, desc="Retriving data", total = len(days)) :
    
    result = breeze.get_historical_data_v2(interval= "1minute",
                            from_date= startDate,
                            to_date= endDate,
                            stock_code= instrument,
                            exchange_code= exchage_code[0],
                            product_type= segment[0])
    
    successResult = result['Success']
    if len(successResult) != 0:
        daf = pd.DataFrame(successResult)
        priceDf = priceDf.append(daf)

    # Increment the date by one day.
    startDate = startDate + timedelta(days=2)
    endDate = endDate + timedelta(days=2) 
    
    if startDate > stopDate :
        break
    
    if priceDf.empty:
        continue

priceDf['Instrument'] = priceDf['stock_code']
priceDf.drop(['stock_code'], axis=1, inplace=True)
priceDf.drop(['exchange_code'], axis=1, inplace = True)
priceDf.rename(columns = {'open':'Open'}, inplace = True)
priceDf.rename(columns = {'high':'High'}, inplace = True)
priceDf.rename(columns = {'low':'Low'}, inplace = True)
priceDf.rename(columns = {'close':'Close'}, inplace = True)
priceDf.rename(columns = {'volume':'Volume'}, inplace = True)
priceDf.rename(columns = {'datetime':'Date'}, inplace = True)
#priceDf.rename(columns = {'open_interest':'OpenInterest'}, inplace = True)

priceDf = priceDf[['Instrument','Date','Open','High','Low','Close','Volume']]
priceDf = priceDf.reset_index()
priceDf.drop(['index'], axis=1, inplace = True)
priceDf['Instrument'] = "FINNIFTY"
#print(priceDf['Date'].iloc[-1])
#priceDf.to_csv("G:\\andyvoid\\data\quotes\\csv_database\\nifty\\options\\2023\\" + fileName.upper() +".csv", index= False)
#completedIndex = i

priceDf.to_csv("G:\\andyvoid\\data\quotes\\csv_database\\finnifty\\indices\\" + "Finnifty_2023_11_18" + ".csv", index= False)

#%%

""" THIS SECTION IS TO RETRIVE ICICI BANK OPTIONS DATA """
#Ticker or Instrument ,Date,Open,High,Low,Close,Volume,Open Interest

allStrikesDf = pd.read_csv("G:\\andyvoid\\data\\quotes\\bhav\\finnifty\\finnifty_2023_CEPE_2024_feb_all_traded_days.csv")
allStrikesDf['expiry'] = pd.to_datetime(allStrikesDf['EXPIRY_DT'])
allStrikesDf = allStrikesDf[allStrikesDf['STRIKE_PR'] != 0]

#%%
#NIFFIN 
#CNXBAN
#NIFTY
instrument = "NIFFIN"
segment = ["cash","options"]
exchage_code = ["NSE","NFO"]
requestTimeOutSleep = 2
completedIndex = 0 - 1



#%%
## This block is to get only the specified file
##BANKNIFTY06JAN2235600CE
# 0,BANKNIFTY06JAN2235500CE,Dataframe Empty
# 1,BANKNIFTY06JAN2236700CE,Dataframe Empty
# 2,BANKNIFTY06JAN2236600CE,Dataframe Empty
# 3,BANKNIFTY06JAN2237100CE,Dataframe Empty
# 4,BANKNIFTY06JAN2237000CE,Dataframe Empty
# 5,BANKNIFTY06JAN2237300CE,Dataframe Empty
# 6,BANKNIFTY06JAN2237200CE,Dataframe Empty

# 0,BANKNIFTY15MAR1824400CE,Dataframe Empty
# 1,BANKNIFTY15MAR1824300CE,Dataframe Empty
# 2,BANKNIFTY15MAR1824400CE,Dataframe Empty
# 3,BANKNIFTY15MAR1824300CE,Dataframe Empty

#FINNIFTY18JAN2218500PE
#FINNIFTY27DEC2219300PE
allStrikesDf = allStrikesDf.loc[(allStrikesDf['EXPIRY_DT'] == "2022-12-27") & (allStrikesDf['STRIKE_PR'] == 19300.0) & (allStrikesDf['OPTION_TYP'] == "PE")]
completedIndex = 2243 - 1


#%%

for i, row in tqdm(allStrikesDf.iterrows(), desc = "Downloading", total = allStrikesDf.shape[0]): 
    
    if i <= completedIndex:
        continue
    
    if i > 2752 :
        break
    
    print ('Index' + str(i))
 
    expiry = row['expiry']#datetime(2022,1,1,7,0,0)
    priceDf = pd.DataFrame()
    if row['OPTION_TYP'] == "CE":
        option = "call"
    else :
        option = 'put'
    strike = row['STRIKE_PR']
    daysTradedList = row['DaysTraded']
    daysTradedList = literal_eval(daysTradedList)
    #daysLookBack = 100
    #startDate  = expiry - timedelta(days=100)
    #endDate  = startDate + timedelta(1)
    #startDate = startDate.replace(hour = 9, minute = 0, second = 0)
    #endDate = endDate.replace(hour = 15, minute = 35, second = 0)
    
    #days = range(53)
    #for i in tqdm(days, desc="Retriving data", total = len(days)) :
    for date in daysTradedList :
        print(date)
        requestTimeOut = True
        startDate = datetime.strptime(date,"%Y-%m-%d")
        startDate = startDate.replace(hour = 9, minute = 0, second = 0)
        endDate = startDate.replace(hour = 15, minute = 35, second = 0)
        
        while requestTimeOut :
            try :
                print(startDate)
                result = breeze.get_historical_data_v2(interval= "1minute",
                                        from_date= startDate,
                                        to_date= endDate,
                                        stock_code= instrument,
                                        exchange_code= exchage_code[1],
                                        product_type= segment[1],
                                        expiry_date = expiry,
                                        right = option,
                                        strike_price = strike)
                requestTimeOut = False
            except :
                print('Json exception Sleep for 10 seconds')
                time.sleep(requestTimeOutSleep)
                requestTimeOut = True
                
        #print(result)
        
        successResult = result['Success']
        if len(successResult) != 0:
            daf = pd.DataFrame(successResult)
            priceDf = priceDf.append(daf)
    
        # Increment the date by one day.
        #startDate = startDate + timedelta(days=2)
        #endDate = endDate + timedelta(days=2)
        
    if priceDf.empty:
        print("\ndataframe empty")
        continue

    priceDf['Instrument'] = priceDf['stock_code']
    priceDf.drop(['stock_code'], axis=1, inplace=True)
    priceDf.drop(['exchange_code'], axis=1, inplace = True)
    priceDf.rename(columns = {'open':'Open'}, inplace = True)
    priceDf.rename(columns = {'high':'High'}, inplace = True)
    priceDf.rename(columns = {'low':'Low'}, inplace = True)
    priceDf.rename(columns = {'close':'Close'}, inplace = True)
    priceDf.rename(columns = {'volume':'Volume'}, inplace = True)
    priceDf.rename(columns = {'datetime':'Date'}, inplace = True)
    priceDf.rename(columns = {'open_interest':'OpenInterest'}, inplace = True)

    priceDf = priceDf[['Instrument','Date','Open','High','Low','Close','Volume','OpenInterest']]
    priceDf = priceDf.reset_index()
    priceDf.drop(['index'], axis=1, inplace = True)
    priceDf['Instrument'] = "FINNIFTY"
    #print(priceDf['Date'].iloc[-1])
    fileName = row['SYMBOL'] + expiry.strftime("%d%b%y") + str(int(strike)) + row['OPTION_TYP']
    priceDf.to_csv("G:\\andyvoid\\data\\quotes\\csv_database\\FINNIFTY\\options\\temp\\" + fileName.upper() +".csv", index= False)

    completedIndex = i

#os.system("shutdown /s /t 1") 
    
#%% CLeaning of Data







    






# Generate ISO8601 Date/DateTime String
# iso_date_string = dt.datetime.strptime("28/02/2021","%d/%m/%Y").isoformat()[:10] + 'T05:30:00.000Z'
# iso_date_time_string = dt.datetime.strptime("28/02/2021 23:59:59","%d/%m/%Y %H:%M:%S").isoformat()[:19] + '.000Z'



