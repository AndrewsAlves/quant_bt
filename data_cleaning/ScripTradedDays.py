import pandas as pd
import datetime as dt
from tqdm import tqdm

nifty = pd.read_csv("G:\\andyvoid\\data\\quotes\\bhav\\finnifty\\finnifty_derivatives_2022.csv")
nifty2 = pd.read_csv("G:\\andyvoid\\data\\quotes\\bhav\\finnifty\\finnifty_derivatives_2023.csv")

niftyBhav = nifty.append(nifty2)
#niftyBhav = nifty
niftyBhav['Date'] = pd.to_datetime(niftyBhav['TIMESTAMP'], format = "%Y-%m-%d")
niftyBhav['EXPIRY_DT'] = pd.to_datetime(niftyBhav['EXPIRY_DT'], format = "%d-%b-%Y")
niftyDailyBhav = niftyBhav.groupby('Date')

tradedDays = niftyBhav['Date']
tradedDays.drop_duplicates(keep = 'first', inplace= True)
tradedDays = tradedDays.reset_index()
tradedDays.drop('index', axis = 1)

niftyOptionTickers = pd.read_csv("G:\\andyvoid\\data\\quotes\\bhav\\finnifty\\finnifty_2023_CEPE_AllStrikes.csv")
niftyOptionTickers['EXPIRY_DT'] = pd.to_datetime(niftyOptionTickers['EXPIRY_DT'], format = "%Y-%m-%d")
#%%
tickerTradedDayList = []

for index, row in tqdm(niftyOptionTickers.iterrows(), desc = "Scanning...", total = niftyOptionTickers.shape[0]) :

    symbol = row['SYMBOL']
    strike = row['STRIKE_PR']
    expiryDay = row['EXPIRY_DT']
    optionType = row['OPTION_TYP']
    
    tickerDays = []

    startDate = expiryDay - dt.timedelta(days=100)
    daysToIterate = tradedDays.loc[(tradedDays['Date'] >= startDate)
                                   & (tradedDays['Date'] <= expiryDay)]

    for index, row in daysToIterate.iterrows() : 
        
        date = row['Date']
        
        if date < (expiryDay - dt.timedelta(days=100)) : 
            continue
        
        if date > expiryDay :
            break
        
        dateDf = niftyDailyBhav.get_group(date)
        tickerDetails = dateDf.loc[(dateDf['SYMBOL'] == symbol)
                                   & (dateDf['EXPIRY_DT'] == expiryDay)
                                   & (dateDf['STRIKE_PR'] == strike)
                                   & (dateDf['OPTION_TYP'] == optionType)]
        if not tickerDetails.empty :
            if tickerDetails['CONTRACTS'].iloc[0] != 0 :
                tickerDays.append(date)
                
        # if tickerDetails.empty :
        #     print("\n" + symbol + str(strike) + " " + expiryDay.strftime("%d-%b-%Y") + str(optionType) + "Not found in date" + date.strftime("%d-%b-%Y"))
        # elif tickerDetails['CONTRACTS'].iloc[0] != 0 :
        #     print("\n" + symbol + str(strike) + " " + expiryDay.strftime("%d-%b-%Y") + str(optionType) + "found in date" + date.strftime("%d-%b-%Y"))
        #     tickerDays.append(date)
        # else :
        #     print("\n" + symbol + str(strike) + " " + expiryDay.strftime("%d-%b-%Y") + str(optionType) + "Not Traded in date" + date.strftime("%d-%b-%Y"))

    print('\nTotal Days traded for ticker' + symbol + str(strike) + " " + expiryDay.strftime("%d-%b-%Y") + str(optionType) + " - " + str(len(tickerDays)))
    tickerTradedDayList.append(tickerDays)
    
#%%
dummy = tickerTradedDayList.copy()
#%%
for item in dummy:
    for idx , date in enumerate(item):
        item[idx] = date.strftime("%Y-%m-%d") 
        
#%%
niftyOptionTickers['DaysTraded'] = dummy
niftyOptionTickers.to_csv("G:\\andyvoid\\data\\quotes\\bhav\\finnifty\\finnifty_2023_CEPE_AllStrikes_traded_dates.csv", index = False)

            
    
        
