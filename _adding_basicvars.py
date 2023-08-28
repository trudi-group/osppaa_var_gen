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

def add_returns(self):
    for coin_name in self.coindata.keys():

        prices = self.coindata[coin_name].filter(like = self.price_var)

        returns = prices / prices.shift(-1) - 1
        ret_lead = prices.shift(+1) / prices - 1
        p_lead = prices.shift(+1)

        returns = returns.rename(columns = {self.price_var : "returns"})
        ret_lead = ret_lead.rename(columns = {self.price_var : "ret_lead"})
        p_lead = p_lead.rename(columns = {self.price_var : "p_lead"})

        self.coindata[coin_name] = pd.concat([self.coindata[coin_name], returns, ret_lead, p_lead], axis=1)
        print("|---| Added returns for: |---| "+ coin_name)

        
def add_stablecoin_identifier(self):
    stablecs   = self.config[self.source_sc_ids]["stablecoin_ids"]
    for coin_name in self.coindata.keys():
        if coin_name in stablecs:
            is_stablec = 1
        else:
            is_stablec = 0 
        dummyvar   = [is_stablec]*(self.coindata[coin_name].shape[0])
        dummyvar   = pd.DataFrame({"is_stablecoin" : dummyvar})
        self.coindata[coin_name] = pd.concat([self.coindata[coin_name].reset_index(drop=True), dummyvar], axis=1)
        print("|---| Added stablecoin dummy for: |---| "+ coin_name)


def add_supply(self):
    for coin_name in self.coindata.keys():

        market_caps = self.coindata[coin_name].market_caps
        prices = self.coindata[coin_name].prices

        csupply = market_caps / prices
        csupply = csupply.to_frame(name = "csupply")
        
        self.coindata[coin_name] = pd.concat([self.coindata[coin_name], csupply], axis=1)
        print("|---| Added csupply for: |---| "+ coin_name)
