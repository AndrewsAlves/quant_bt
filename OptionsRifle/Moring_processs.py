# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 11:26:59 2023

@author: Admin
"""

from kiteconnect import KiteConnect
import webbrowser
import pandas as pd
import datetime as dt

API_KEY= "yzczdzxsmw9w9tq9"
API_SECRET = "2k7oo9x1w0xl5g9789wl8j6v4u03lq0x"

KEY_NIFTYBANK = "NIFTY BANK"
KEY_BANKNIFTY_FUT = "BANKNIFTY"
KEY_CE = "CE"
KEY_PE = "PE"
KEY_FUT = "FUT"
KEY_EQ = "EQ"



class KiteApi() :
    __instance = None

    def __init__(self) : 
        self.kite = KiteConnect(api_key=API_KEY)    
        self.upcomingFutureExpiry = None
        self.upcomingOptionsExpiry = None
        
    def openLoginUrl(self) :
        webbrowser.open_new(self.kite.login_url())
        return 
    
    def generateSession(self, requestToken) : 
        data = self.kite.generate_session(requestToken, api_secret=API_SECRET)
        access_token = data["access_token"]
        self.kite.set_access_token(access_token)
        print("Request Token : " + requestToken)
        print("Access Token : " + access_token)
        return

    @staticmethod
    def getInstance() :
        if KiteApi.__instance is None:
           KiteApi.__instance = KiteApi()
        return KiteApi.__instance
    
    
    def getInstruments(self) :
        instrumentList = self.kite.instruments()

        instrumentMain = []
        banknifty_instrumenttk = []
        for instrument in instrumentList: 
            if "INDICES" in instrument["segment"] and "NIFTY BANK" in instrument["tradingsymbol"]:
                instrumentMain.append(instrument)
            if "FUT" in instrument["instrument_type"] and "BANKNIFTY" in instrument["tradingsymbol"]:
                banknifty_instrumenttk.append(instrument)
            if "CE" in instrument["instrument_type"] and "BANKNIFTY" in instrument["tradingsymbol"]:
                banknifty_instrumenttk.append(instrument)
            if "PE" in instrument["instrument_type"] and "BANKNIFTY" in instrument["tradingsymbol"]:
                banknifty_instrumenttk.append(instrument)    

        niftyBankInstruments = pd.DataFrame(banknifty_instrumenttk)
        self.upcomingFutureExpiry = niftyBankInstruments.loc[niftyBankInstruments['instrument_type'] == "FUT"]['expiry'].min()
        self.upcomingOptionsExpiry = niftyBankInstruments.loc[(niftyBankInstruments['instrument_type'] == "CE") | (niftyBankInstruments['instrument_type'] == "PE")]['expiry'].min()
        
        requiredInstrumentsFut = niftyBankInstruments.loc[(niftyBankInstruments['instrument_type'] == "FUT") & (niftyBankInstruments['expiry'] == self.upcomingFutureExpiry)]
        requiredInstrumentsOpt = niftyBankInstruments.loc[((niftyBankInstruments['instrument_type'] == "CE") | (niftyBankInstruments['instrument_type'] == "PE")) & (niftyBankInstruments['expiry'] == self.upcomingOptionsExpiry)]
        
        instrumentMainDf = pd.DataFrame(instrumentMain)
        instrumentMainDf = instrumentMainDf.append(requiredInstrumentsFut)
        instrumentMainDf = instrumentMainDf.append(requiredInstrumentsOpt)

        print(self.upcomingFutureExpiry)
        print(self.upcomingOptionsExpiry)
        
        d1 = dt.date.today().strftime("%d-%m-%Y")
        filename = d1+"_instrument_list.csv"

        ##requiredInstrumentDF.to_csv("G:\\andyvoid\\projects\\andyvoid_tools\\options_rifle\\database\\" + filename, index= False)
        
        instrumentMainDf['expiry'] = pd.to_datetime(instrumentMainDf['expiry'])
        self.upcomingOptionsExpiry = pd.to_datetime(self.upcomingOptionsExpiry)
        self.upcomingFutureExpiry = pd.to_datetime(self.upcomingFutureExpiry)

        
        return instrumentMainDf
        

df = KiteApi.getInstance().getInstruments()
optionsdf = df.loc[(df['instrument_type'] == "CE") | (df['instrument_type'] == "PE")]

# KEY_NIFTYBANK = "NIFTY BANK"
# KEY_BANKNIFTY_FUT = "BANKNIFTY"
# KEY_CE = "CE"
# KEY_PE = "PE"
# KEY_FUT = "FUT"
# KEY_EQ = "EQ"

# step1 = None

# def getInstrumentToken(name = "", instrumentType = KEY_EQ, expiry = "", strike = 0) :
#         tokenId = 0
#         if instrumentType == KEY_EQ : 
#             dfi = df.loc[(df['name'] == name) & (df['instrument_type'] == instrumentType)]
#             tokenId = dfi['instrument_token']
#             print(df)
#         elif instrumentType == KEY_FUT:
#             dfi = df.loc[(df['name'] == name) & (df['instrument_type'] == instrumentType)]
#             print(dfi['expiry'].dtype)
#             df2 = dfi.loc[dfi['expiry'] == expiry]
#             tokenId = df2['instrument_token']
#         elif instrumentType == KEY_CE or instrumentType == KEY_PE :
#             dfi = df.loc[(df['name'] == name) & (df['instrument_type'] == instrumentType)]
#             df2 = dfi.loc[(dfi['expiry'] == expiry) & (dfi['strike'] == strike)]
#             tokenId = df2['instrument_token']
        
#         return tokenId

# # upcomingOptionsExpiry = pd.to_datetime(KiteApi.getInstance().upcomingOptionsExpiry)
# # print(upcomingOptionsExpiry)

# token = getInstrumentToken(name = "BANKNIFTY", instrumentType=KEY_CE, expiry = KiteApi.getInstance().upcomingOptionsExpiry, strike = 38600)
# print(token)
# print(KiteApi.getInstance().upcomingOptionsExpiry)
# upcomingFuturesExpiryDf = df
# upcomingFutureExpiry = upcomingFuturesExpiryDf.loc[upcomingFuturesExpiryDf['instrument_type'] == "FUT"]['expiry'].min()
# upcomingOptionsExpiry = upcomingFuturesExpiryDf.loc[(upcomingFuturesExpiryDf['instrument_type'] == "CE") | (upcomingFuturesExpiryDf['instrument_type'] == "PE")]['expiry'].min()



