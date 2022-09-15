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


#%%
""" THIS SECTION CLEANES THE SPECIFIED FILES FOR TGE RIGHT DATE TIME STRING FORMAT """
mm_dd_df = pd.read_csv("D:\\andyvoid\data\quotes\After_cleaned\Banknifty\BNF_options\\2020\\08\\BANKNIFTY_NFO_06082020_need_change_slash.csv")
mm_dd_df["Date"] = pd.to_datetime(mm_dd_df["Date"], format= "%d-%m-%Y")
mm_dd_df["Date"] = mm_dd_df["Date"].dt.strftime("%d/%m/%Y")
mm_dd_df.to_csv("D:\\andyvoid\data\quotes\After_cleaned\Banknifty\BNF_options\\2020\\08\\BANKNIFTY_NFO_06082020_changed.csv", index= False)

#%%
""" THIS SECTION CLEANES THE SPECIFIES FILES IN 2021"""

mm_dd_df = pd.read_csv("D:\\andyvoid\data\quotes\After_cleaned\Banknifty\BNF_options\\2021\\10\\BANKNIFTY_NFO_BACKADJUSTED_12102021.csv")
mm_dd_df["Date"] = pd.to_datetime(mm_dd_df["Date"], format = "%d-%m-%Y")
mm_dd_df["Date"] = mm_dd_df["Date"].dt.strftime("%d/%m/%Y")
mm_dd_df.to_csv("D:\\andyvoid\data\quotes\After_cleaned\Banknifty\BNF_options\\2021\\10\\BANKNIFTY_NFO_BACKADJUSTED_12102021_changed.csv", index= False)

#%%

""" THIS SECTION CLEANES THE .NFO STRING FROM THE TICKER STRING """

bnf_op_path = "D:\\andyvoid\data\quotes\After_cleaned\Banknifty\BNF_options"

#df = pd.read_csv(bnf_op_path + "\\" + "2021" + "\\" + "01" + "\\" + "BANKNIFTY_NFO_BACKADJUSTED_04012021.csv", parse_dates=True)
#df["Ticker"] = df["Ticker"].str.replace(".NFO", "")


def getOptionsData(year) :
    month_fol = os.listdir(bnf_op_path + "\\" + year)
    opdf = pd.DataFrame()
    ##Reading options data and using a tqdm Progress bar 
    for month in month_fol : 
       fnofiles = os.listdir(bnf_op_path + "\\" + year + "\\" + month)
       for file in tqdm(fnofiles, desc="Reading Options data - " + month + " " + year):
           df = pd.read_csv(bnf_op_path + "\\" + year + "\\" + month + "\\" + file, parse_dates=True)
           df["Ticker"] = df["Ticker"].str.replace(".NFO", "")
           df.to_csv(bnf_op_path + "\\" + year + "_changed" + "\\" + month + "\\" + file, index = False)
           #print(opdf)
    return opdf    

getOptionsData("2021")
