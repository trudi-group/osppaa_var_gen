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

def load_data(self,
              coindata_dir):
    dtalist = list()
    for file in self.coindata_files:
        dta_raw = pd.read_csv(coindata_dir+file)
        dta = dta_raw[::-1].reset_index(drop=True)
        dtalist.append(dta)
        print("|---| Loaded : |---| " + file)
    return(dtalist)

def load_yfinance_data(self,
                       path,
                       name):
    yfdata = helpers.load_obj(name = name,
                              path = path)
    print("|---| Loaded : |---| " + path + name)
    return(yfdata)

def load_crix_data(self,
                   path,
                   name):
    crixdata = helpers.load_obj(name = name,
                              path = path)
    print("|---| Loaded : |---| " + path + name)
    return(crixdata)


def load_cmi10_data(self,
                   path,
                   name):
    cmi10data = helpers.load_obj(name = name,
                                 path = path)
    print("|---| Loaded : |---| " + path + name)
    return(cmi10data)
