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

def add_volatility_squaredreturns(self):
    for coin_name in self.coindata.keys():
        returns = self.coindata[coin_name].filter(like = "returns")
        volatility = returns.pow(2)
        volatility = volatility.rename(columns = {"returns" : "V_volatility_sr"})
        self.coindata[coin_name] = pd.concat([self.coindata[coin_name], volatility], axis=1)
        print("|---| Added volatility (squared returns) for: |---| "+ coin_name)


def add_volatility_windowSD(self, wlength, sd_minobs):

    # Input either from config file or specified in arguments
    if wlength == "from_config":
        wlength = self.config["dataloading"]["volatility_sd_windowlength"]
    elif not type(wlength) == int:
        raise TypeError("Input has to be an integer.")

    # Input either from config file or specified in arguments
    if sd_minobs == "from_config":
        sd_minobs = self.config["dataloading"]["volatility_sd_minobs"]
    elif not type(sd_minobs) == int:
        raise TypeError("Input has to be an integer.")


    for coin_name in self.coindata.keys():
        returns = self.coindata[coin_name]["returns"]

        vola_dta = [returns[w_start:w_start+wlength] for w_start in range(len(returns))]
        volatility = [element.std(skipna = True) if len(element) >= sd_minobs else np.nan for element in vola_dta]
        volatility = { 'V_volatility_st_'+ str(wlength): volatility} 
        volatility = pd.DataFrame(volatility)
        
        self.coindata[coin_name] = pd.concat([self.coindata[coin_name], volatility], axis=1)

        print("|---| Added volatility (windowlength = "
              + str(wlength)
              +") for: |---| "
              + coin_name)

def _SD_for_dframelist(dfs_list, minobs):
    vola = list()
    for element in dfs_list:
        if len(element) >= minobs:
            vola.append(element.std(skipna = True))
        else:
            vola.append(np.nan)
    return vola

def _make_dframelist(vec, windowlength):
    dframelist = [vec[start:start+windowlength] for start in range(len(vec))]
    return dframelist

def add_volatility_ratio(self, wlength_st, wlength_lt, sd_minobs):

    # Input either from config file or specified in arguments
    if wlength_st == "from_config":
        wlength = self.config["dataloading"]["volatility_ratio_wlength_st"]
    elif not type(wlength_st) == int:
        raise TypeError("Input has to be an integer.")

    # Input either from config file or specified in arguments
    if wlength_lt == "from_config":
        wlength = self.config["dataloading"]["volatility_ratio_wlength_lt"]
    elif not type(wlength_lt) == int:
        raise TypeError("Input has to be an integer.")

    # Input either from config file or specified in arguments
    if sd_minobs == "from_config":
        sd_minobs = self.config["dataloading"]["volatility_ratio_minobs"]
    elif not type(sd_minobs) == int:
        raise TypeError("Input has to be an integer.")


    for coin_name in self.coindata.keys():
        returns = self.coindata[coin_name]["returns"]

        vola_dta_lt = _make_dframelist(vec   = returns,
                                       windowlength = wlength_lt)
        vola_dta_st = _make_dframelist(vec   = returns,
                                       windowlength = wlength_st)
        vola_lt = _SD_for_dframelist(dfs_list = vola_dta_lt,
                                     minobs = sd_minobs)
        vola_st = _SD_for_dframelist(dfs_list = vola_dta_st,
                                     minobs = sd_minobs)
        vola_ratio = [vola_st[i]/vola_lt[i] for i in range(len(returns))]
        vola_ratio = { 'V_volatility_ratio_'+ str(wlength_st) + "_" + str(wlength_lt): vola_ratio} 
        vola_ratio = pd.DataFrame(vola_ratio)
        
        self.coindata[coin_name] = pd.concat([self.coindata[coin_name], vola_ratio], axis=1)

        print("|---| Added volatility ratio(windowlength = "
              + str(wlength_st)
              + "/"
              + str(wlength_lt)
              +") for: |---| "
              + coin_name)
