# TO BE CLEANED -----------------------------

# Modules
import pandas as pd
import os as os
import statistics as stcs
import numpy as np
import itertools as itr
import pandas as pd
import statsmodels.formula.api as sm
import datetime
import yaml
import importlib
#temp
import matplotlib.pyplot as plt

# Import SETTINGS-file
with open("./SETTINGS.yml", 'r') as stream:
    try:
        SETTINGS = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

# Import helpers
spec    = importlib.util.spec_from_file_location("noname", "./gen_helpers.py")
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)

# ----------------------------------

def mergeCRIX(self):
    for cname in self.coindata.keys():
        adddata = self.crixdata
        maindata = self.coindata[cname]
        
        mergeddata = pd.merge(maindata,
                              adddata,
                              on="time")
        
        self.coindata[cname] = mergeddata

def mergeCMI10(self):
    for cname in self.coindata.keys():
        """         adddata = self.yfinancedata["CMI10.SW"].copy()
        adddata["time"] = pd.to_datetime(adddata["time"])
        adddata["cp"]   = adddata["cp"].apply(np.sqrt).apply(np.sqrt)
        adddata.rename(columns={"cp": "vola_cmi10"}, inplace=True)
        maindata = self.coindata[cname].copy()
        
        mergeddata = pd.merge(maindata,
                              adddata,
                              how="left", 
                              on="time")
        self.coindata[cname] = mergeddata """
        adddata = self.yfinancedata["BTC-USD"].copy()
        adddata["time"] = pd.to_datetime(adddata["time"])
        adddata["cp"]   = adddata["cp"].apply(np.sqrt).apply(np.sqrt)
        adddata.rename(columns={"cp": "vola_btc"}, inplace=True)
        maindata = self.coindata[cname].copy()
        
        mergeddata = pd.merge(maindata,
                              adddata,
                              how="left", 
                              on="time")
        
        self.coindata[cname] = mergeddata

        adddata = self.yfinancedata["ETH-USD"].copy()
        adddata["time"] = pd.to_datetime(adddata["time"])
        adddata["cp"]   = adddata["cp"].apply(np.sqrt).apply(np.sqrt)
        adddata.rename(columns={"cp": "vola_eth"}, inplace=True)
        maindata = self.coindata[cname].copy()
        
        mergeddata = pd.merge(maindata,
                              adddata,
                              how="left", 
                              on="time")

        self.coindata[cname] = mergeddata


        adddata = self.yfinancedata["XRP-USD"].copy()
        adddata["time"] = pd.to_datetime(adddata["time"])
        adddata["cp"]   = adddata["cp"].apply(np.sqrt).apply(np.sqrt)
        adddata.rename(columns={"cp": "vola_xrp"}, inplace=True)
        maindata = self.coindata[cname].copy()
        
        mergeddata = pd.merge(maindata,
                              adddata,
                              how="left", 
                              on="time")
        
        self.coindata[cname] = mergeddata
        
        adddata = self.yfinancedata["GAS-ETH"].copy()
        adddata["time"] = pd.to_datetime(adddata["time"])
        adddata["cp"]   = adddata["cp"]
        adddata.rename(columns={"cp": "gas"}, inplace=True)
        maindata = self.coindata[cname].copy()
        
        mergeddata = pd.merge(maindata,
                              adddata,
                              how="left", 
                              on="time")        
        self.coindata[cname] = mergeddata




