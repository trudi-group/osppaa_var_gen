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
import scipy
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

def coindata_list_to_dictonary(self):
    # Create a dictionary from zip object
    self.list_zip   = zip(self.coindata_names_original,
                          self.coindata)
    list_dict = dict(self.list_zip)

    return(list_dict)

def clean_date(self):
    for coin_name in self.coindata.keys():

        self.coindata[coin_name]["time"] = pd.to_datetime(self.coindata[coin_name]["time"])

        print("|---| Cleaned date for: |---| "+ coin_name)

def _zscore_for_pd(pd_col,
                   stdev_degrees_of_free):
    zscores = (pd_col - pd_col.mean())/pd_col.std(ddof=stdev_degrees_of_free)
    return zscores

def _norm_for_pd(pd_col):
    norm = (pd_col - pd_col.min())/(pd_col.max()-pd_col.min())
    return norm

def _return_missing_val_percentage(self,
                                   cname):
    missval = self.coindata[cname].isnull().sum().sum()
    totalval = (self.coindata[cname].shape[0]*self.coindata[cname].shape[1])
    missvalperc = round(missval*100/totalval)
    return missvalperc
                

def remove_nan_lines(self,
                     thresh     = "from_config",
                     ignorecols = "from_config"):
    # Input either from config file or specified in arguments
    if thresh == "from_config":
        thresh = self.config["dataloading"]["na_cleaning_heads_and_tails_threshold"]
    elif not type(thresh) == int:
        raise TypeError("Input has to be an integer.")

    # Input either from config file or specified in arguments
    if thresh == "from_config":
        ignorecols = self.config["dataloading"]["na_cleaning_heads_and_tails_ignorecols"]
    elif any([col not in self.coindata["tether"].keys() for col in ignorecols]):
        raise TypeError("At least one column in the list does not exist.")

    for coin_name in self.coindata.keys():
        cdta                                = self.coindata[coin_name].drop(ignorecols, axis    = 1)
        head_and_tail_select                = ([True]*thresh
                                               + [False]*(len(cdta)-2*thresh)
                                               + [True]*thresh)
        row_has_nan                         = cdta.isnull().any(axis=1)
        remove_select_zip = zip(head_and_tail_select, row_has_nan)
        remove_select = [not (z[0] and z[1]) for z in remove_select_zip] 
        self.coindata[coin_name]  = self.coindata[coin_name].iloc[remove_select, :]
        
        if len(self.coindata[coin_name].dropna()) != len(self.coindata[coin_name]):
            print("|---| WARNING: Still " +
                  str(self._return_missing_val_percentage(coin_name)) +
                  " percent of NaNs in: |---| " +
                  coin_name)
        
        print("|---| Removed NaNs in heads and tails for: |---| " + coin_name)

def drop_dta_with_many_nas(self,
                     thresh = "from_config"):
    # Input either from config file or specified in arguments
    if thresh == "from_config":
        thresh = self.config["dataloading"]["max_na_threshold"]
    elif not type(thresh) == int:
        raise TypeError("Input has to be an integer.")

    # Create a vector of sum
    nas = [sum(self.coindata[c][self.price_var].isna()) for c in self.coindata.keys()]
    bool_filter = [i < thresh for i in nas]
    dta = list(itr.compress(self.coindata.values(), bool_filter))
    nms = list(itr.compress(self.coindata.keys(), bool_filter))
    dct = helpers.list_to_dictonary(names    = nms,
                                    datalist = dta)
    self.coindata = dct
    print("|---| Removed timeseries with more than " +
          str(thresh) +
          " NAs head and tails.|---| ")

def drop_dta_with_few_obs(self,
                          thresh = "from_config"):
    # Input either from config file or specified in arguments
    if thresh == "from_config":
        thresh = self.config["dataloading"]["min_rows_threshold"]
    elif not type(thresh) == int:
        raise TypeError("Input has to be an integer.")

    # Create a vector of sum
    nrows = [self.coindata[c].shape[0] for c in self.coindata.keys()]
    bool_filter = [i > thresh for i in nrows]
    dta   = list(itr.compress(self.coindata.values(), bool_filter))
    nms   = list(itr.compress(self.coindata.keys(), bool_filter))
    dct   = helpers.list_to_dictonary(names    = nms,
                                      datalist = dta)
    self.coindata = dct
    print("|---| Removed timeseries with less then " +
          str(thresh) +
          " observations.|---| ")


def drop_dta_with_low_volume(self,
                             thresh = "from_config"):
    # Input either from config file or specified in arguments
    if thresh == "from_config":
        thresh = self.config["dataloading"]["min_vol_threshold"]
    elif not type(thresh) == int:
        raise TypeError("Input has to be an integer.")

    # Create a vector of sum
    vol = [self.coindata[c].total_volumes.head(1).values for c in self.coindata.keys()]
    bool_filter = [i > thresh for i in vol]
    dta   = list(itr.compress(self.coindata.values(), bool_filter))
    nms   = list(itr.compress(self.coindata.keys(), bool_filter))
    dct   = helpers.list_to_dictonary(names    = nms,
                                      datalist = dta)
    self.coindata = dct
    print("|---| Removed timeseries with a volume less then " +
          str(thresh) +
          " USD.|---| ")


def drop_dta_with_low_mcap(self,
                           thresh = "from_config"):
    # Input either from config file or specified in arguments
    if thresh == "from_config":
        thresh = self.config["dataloading"]["min_mcap_threshold"]
    elif not type(thresh) == int:
        raise TypeError("Input has to be an integer.")

    # Create a vector of sum
    mcap = [self.coindata[c].market_caps.head(1).values for c in self.coindata.keys()]
    bool_filter = [i > thresh for i in mcap]
    dta   = list(itr.compress(self.coindata.values(), bool_filter))
    nms   = list(itr.compress(self.coindata.keys(), bool_filter))
    dct   = helpers.list_to_dictonary(names    = nms,
                                      datalist = dta)
    self.coindata = dct
    print("|---| Removed timeseries with a marketcap less then " +
          str(thresh) +
          " USD.|---| ")


        
def truncate_outliers(self,
                      cols   = "from_config",
                      thresh = "from_config"):
        # Input either from config file or specified in arguments
    if thresh == "from_config":
        thresh = self.config["dataloading"]["outlier_threshold_for_zscore"]
    elif not type(thresh) == int:
        raise TypeError("Input has to be an integer.")

    if cols == "from_config":
        cols = self.config["dataloading"]["outlier_cols_to_be_treated"]
    
    for coin_name in self.coindata.keys():
        for col in cols:
            threshval_neg = (self.coindata[coin_name].loc[:,[col]].mean() - self.coindata[coin_name].loc[:,[col]].std(ddof=1))*thresh
            threshval_pos = (self.coindata[coin_name].loc[:,[col]].mean() + self.coindata[coin_name].loc[:,[col]].std(ddof=1))*thresh
            coldta    = self.coindata[coin_name][col]
            zscores   = _zscore_for_pd(pd_col = coldta,
                                       stdev_degrees_of_free = 1) # Bessels correction for sample stdev
            is_outl_neg   = zscores < -thresh
            is_outl_pos   = zscores > thresh
            self.coindata[coin_name].loc[is_outl_neg, [col]] = threshval_neg[0] # python sucks 
            self.coindata[coin_name].loc[is_outl_pos, [col]] = threshval_pos[0] # [0] for value from series of len = 0

            print("|---| Truncated outliers for column: " +
                  str(col)+
                " for: |---| " + coin_name)

def normalize_data_by_col(self,
                          cols   = "from_config",
                          typ    = "from_config"):
    # Input either from config file or specified in arguments
    if typ == "from_config":
        typ = self.config["dataloading"]["normalization_type"]
    elif not typ in ["normalization", "standardization"]:
        raise TypeError("Input has to be either 'standardization' or 'normalization'.")

    if cols == "from_config":
        cols = self.config["dataloading"]["normalization_columns"]
        
    for coin_name in self.coindata.keys():
        for col in cols:
            coldta      = self.coindata[coin_name][col]
            if(typ == "standardization"):
                zscores   = _zscore_for_pd(pd_col = coldta,
                                           stdev_degrees_of_free = 1) # Bessels correction for sample stdev
                self.coindata[coin_name].loc[:, [col]] = zscores
            elif(typ == "normalization"):
                normalized   = _norm_for_pd(pd_col = coldta) # Bessels correction for sample stdev
                self.coindata[coin_name].loc[:, [col]] = normalized

        print("|---| Normalized data for : |---| " + coin_name)
