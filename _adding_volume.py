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


def add_volume_ratio(self, wlength_st, wlength_lt, sd_minobs):

    # Input either from config file or specified in arguments
    if wlength_st == "from_config":
        wlength = self.config["dataloading"]["volume_ratio_wlength_st"]
    elif not type(wlength_st) == int:
        raise TypeError("Input has to be an integer.")

    # Input either from config file or specified in arguments
    if wlength_lt == "from_config":
        wlength = self.config["dataloading"]["volume_ratio_wlength_lt"]
    elif not type(wlength_lt) == int:
        raise TypeError("Input has to be an integer.")

    # Input either from config file or specified in arguments
    if sd_minobs == "from_config":
        sd_minobs = self.config["dataloading"]["volume_ratio_minobs"]
    elif not type(sd_minobs) == int:
        raise TypeError("Input has to be an integer.")


    for coin_name in self.coindata.keys():
        volume = self.coindata[coin_name]["total_volumes"]

        volume_dta_lt = _make_dframelist(vec   = volume,
                                       windowlength = wlength_lt)
        volume_dta_st = _make_dframelist(vec   = volume,
                                       windowlength = wlength_st)
        volume_lt = _SD_for_dframelist(dfs_list = volume_dta_lt,
                                     minobs = sd_minobs)
        volume_st = _SD_for_dframelist(dfs_list = volume_dta_st,
                                     minobs = sd_minobs)
        volume_ratio = [volume_st[i]/volume_lt[i] for i in range(len(volume))]
        volume_ratio = { 'V_volume_ratio_'+ str(wlength_st) + "_" + str(wlength_lt): volume_ratio} 
        volume_ratio = pd.DataFrame(volume_ratio)
        
        self.coindata[coin_name] = pd.concat([self.coindata[coin_name], volume_ratio], axis=1)

        print("|---| Added volume ratio(windowlength = "
              + str(wlength_st)
              + "/"
              + str(wlength_lt)
              +") for: |---| "
              + coin_name)
