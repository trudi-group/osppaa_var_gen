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

def add_resistance(self,
                   window_prd1_start      = "from_config",
                   window_prd1_end        = "from_config",
                   window_prd2_start      = "from_config",
                   window_prd2_end        = "from_config",
                   resistance_sensitivity = "from_config"):

    # Input either from config file or specified in arguments
    if window_prd1_start == "from_config":
        window_prd1_start = self.config["dataloading"]["resistance_window_prd1_start"]
    elif not type(window_prd1_start) == int:
        raise TypeError("Input has to be an integer.")

    if window_prd1_end == "from_config":
        window_prd1_end = self.config["dataloading"]["resistance_window_prd1_end"]
    elif not type(window_prd1_end) == int:
        raise TypeError("Input has to be an integer.")

    if window_prd2_start == "from_config":
        window_prd2_start = self.config["dataloading"]["resistance_window_prd2_start"]
    elif not type(window_prd2_start) == int:
        raise TypeError("Input has to be an integer.")

    if window_prd2_end == "from_config":
        window_prd2_end = self.config["dataloading"]["resistance_window_prd2_end"]
    elif not type(window_prd2_end) == int:
        raise TypeError("Input has to be an integer.")

    if resistance_sensitivity == "from_config":
        resistance_sensitivity = self.config["dataloading"]["resistance_sensitivity"]
    elif not type(resistance_sensitivity) == int and not type(resistance_sensitivity) == float:
        raise TypeError("Input has to be an integer or float.")

    
    for coin_name in self.coindata.keys():
        # The Resistance factor asks for each day, if the price is at resistance.
        # ... "at resistance" is defined here, usint two dynamic time periods.
        # ... The core is a "high price" selected as the maximum price, during
        # ... a passed period of time (prd1). If now the price has been lower than that
        # ... high price for a certain number of days(leading to prd2) after that past
        # ... period (prd1) has passed and the price today is higher then the high price.
        # ... A price can be at resistance for several days or not. (Caginalp 2014, p.12)

        # 1) Some preparation
        prices = self.coindata[coin_name][self.price_var]           

        # 2) Loop to concatenate decisions per day wrt. if price is at a
        # ... resitance per period 
        resistance = list()
        for t in range(0,len(prices)):

            if (t+window_prd1_start) <= len(prices): # if window_prd1_start > window_prd1_end > ...
                # note: + instead of - as in Caginalp 2014, as we re-ordered timeseries for convenience
                idx_prd1_start = t+window_prd1_start
                idx_prd1_end   = t+window_prd1_end
                idx_prd2_start = t+window_prd2_start
                idx_prd2_end   = t+window_prd2_end

                prices_to_check_prd1 = prices[idx_prd1_end:idx_prd1_start] # reversed as re-ordered timeseries for convenience
                prices_to_check_prd2 = prices[idx_prd2_end:idx_prd2_start]

                high_price = max(prices_to_check_prd1)

                condition_a = all([price <= high_price for price in prices_to_check_prd2])
                condition_b = resistance_sensitivity*high_price <= prices[t] <= high_price

                price_at_resistance = 1 if condition_a and condition_b else 0

                resistance.append(price_at_resistance)
            else:
                resistance.append(np.nan)

        resistance = { 'V_resistance'
                       + "_w1f_" + str(window_prd1_start)
                       + "_w1t_" + str(window_prd1_end)
                       + "_w2f_" + str(window_prd2_start)
                       + "_w2t_" + str(window_prd2_end): resistance} 
        resistance = pd.DataFrame(resistance)

        self.coindata[coin_name] = pd.concat([self.coindata[coin_name],
                                              resistance], axis=1)

        print("|---| Added resistance ("
              + "_w1f_" + str(window_prd1_start)
              + "_w1t_" + str(window_prd1_end)
              + "_w2f_" + str(window_prd2_start)
              + "_w2t_" + str(window_prd2_end)
              +") for: |---| "
              + coin_name)
