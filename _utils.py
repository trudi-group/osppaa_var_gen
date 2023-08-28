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

def get_current_cols(self,
                     coin = "tether",
                     dropcols = []):    
    currentcols = list(self.coindata[coin].columns)
    wantedcols  = [e for e in currentcols if e not in dropcols]
    return(wantedcols)

def na_check(self):    
    na_check = [self.coindata[n].isnull().sum().sum() for n in self.coindata.keys()]
    return(na_check)

def empty_check(self):    
    empty_check = [len(self.coindata[n].isnull()) == 0 for n in self.coindata.keys()]
    return(empty_check)
