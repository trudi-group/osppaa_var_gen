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
import warnings

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


def _make_tuples(self,
                 windowlength,
                 series,
                 trendtype):
    # Note: In "simple" current return is just one normal piece in trend calculation
    # ..... In "sophisticated" current return is benchmark from which others are substracted
    # ..... This makes no difference in creation of tuples but only in add_trend_shortterm()
    tuple_selections_over_time = list()
    for t in range(0,len(series)):

        tuple_selection_for_period = list()
        tuplenumber = windowlength if trendtype == "simple" else windowlength + 1 
        for k in range(0,tuplenumber):#make one tuple extra, as first tuple is for current return
            if t+k+1 < len(series):
                tuple_selection_for_period.append([t+k,t+k+1])

        tuple_selections_over_time.append(tuple_selection_for_period)

    return  tuple_selections_over_time



def add_trend_shortterm(
        self,
        var,
        wlength    = "from_config",
        scalingvar = "from_config",
        minobs     = "from_config",
        trendtype  = "sophisticated"):
    
    # Input either from config file or specified in arguments
    if wlength == "from_config":
        wlength = self.config["dataloading"]["trend_shortterm_windowlength"]
    elif not type(wlength) == int:
        raise TypeError("Input has to be an integer.")
    
    if scalingvar == "from_config":    
        scalingvar = self.config["dataloading"]["trend_shortterm_scaling"]
    elif not type(wlength) == int:
        raise TypeError("Input has to be an integer.")
    
    if minobs == "from_config":    
        minobs = self.config["dataloading"]["trend_shortterm_minobs"]
    elif not type(wlength) == int:
        raise TypeError("Input has to be an integer.")
    
    if trendtype == "from_config":    
        trendtype = self.config["dataloading"]["trend_shortterm_trendtype"]
    elif not trendtype in ["simple","sophisticated"]:
        raise TypeError("Input has to be an integer.")
    
    if not var in [self.price_var,self.vol_var]:    
        raise TypeError("Input has to be price or volume column.")
        
    for coin_name in self.coindata.keys():
        # The trend variable uses weighted sums of historic price changes.
        # This sum is based on the length of the used time window k. 
        # For calculation we adapt Y steps:
        # 1) Prepare some variables used in the later loop
        # 2) Create a list of tuples for selecting elements of the price vector
        # .. that later used to determine *which* historic prices changes are
        # .. part of the summand
        # 3) A nested loop going through every period and within every period
        # .. trough every tuple to select k summands to include for the trend
        # .. value for the respective period. (Caginalp 2014, p.10)

        # 1) Some preparation
        if var == self.price_var:
            basevar = self.coindata[coin_name][self.price_var]
        elif var == self.vol_var:
            basevar = self.coindata[coin_name][self.vol_var]
        else:
            raise TypeError("This should never trigger.")
            
        norm_factor = 1/sum([np.exp(scalingvar*i) for i in range(1,wlength+1)])

        # CASES
        if trendtype == "simple":
            # 2) Selection tuples of indeces for historic price to be part of sum per period
            tuple_selections_over_time  = self._make_tuples(windowlength = wlength,
                                                            series       = basevar,
                                                            trendtype    = "simple")
            # 3) Loop to concatenate weighted sums of price changes per period
            trend = list()
            for tuple_selection_for_period in tuple_selections_over_time:
                cond_sufficient_obs = len(tuple_selection_for_period) >= minobs
                cond_no_zeros = all([False if basevar[tupl[1]] == 0 else True
                                     for tupl in tuple_selection_for_period])
                if cond_sufficient_obs or cond_no_zeros:
                    sum_for_period = 0
                    for k, tupl in enumerate(tuple_selection_for_period):

                        price_updated = basevar[tupl[0]] #"larger" time if it was timestamp
                        price_anchor  = basevar[tupl[1]] #"smaller" time if it was timestamp
                        weight        = np.exp(scalingvar*(k+1))# "+1" as enumerate starts with 0

                        sum_for_period += weight * (
                            (price_updated-price_anchor) / price_anchor
                        )

                    trend.append(norm_factor*sum_for_period)

                else:
                    # otherwise trend is NA fo this period
                    trend.append(np.nan)
        elif trendtype == "sophisticated":
            # 2) Selection tuples of indeces for historic price to be part of sum per period
            tuple_selections_over_time  = self._make_tuples(windowlength = wlength,
                                                            series       = basevar,
                                                            trendtype    = "sophisticated")
            # 3) Loop to concatenate weighted sums of price changes per period
            trend = list()
            for tuple_selection_for_period in tuple_selections_over_time:
                flag_first_tuple = True
                cond_sufficient_obs = len(tuple_selection_for_period) >= minobs
                cond_no_zeros = all([False if basevar[tupl[1]] == 0 else True
                                     for tupl in tuple_selection_for_period])
                if cond_sufficient_obs or cond_no_zeros:
                    sum_for_period = 0
                    for k, tupl in enumerate(tuple_selection_for_period):
                        if flag_first_tuple:
                            price_updated = basevar[tupl[0]] #"larger" time if it was timestamp
                            price_anchor  = basevar[tupl[1]] #"smaller" time if it was timestamp
                            subtrahend_left = (price_updated-price_anchor) / price_anchor
                            flag_first_tuple = False
                        else:

                            price_updated = basevar[tupl[0]] #"larger" time if it was timestamp
                            price_anchor  = basevar[tupl[1]] #"smaller" time if it was timestamp
                            weight        =  np.exp(scalingvar*(k))# "+1" as enumerate starts with 0 but -1 as one tuple for subtrahend_left

                            sum_for_period += weight * (
                                (price_updated-price_anchor) / price_anchor
                            )
                            subtrahend_right_unnormalized = sum_for_period

                    trend.append(subtrahend_left - norm_factor*subtrahend_right_unnormalized)

                else:
                    # otherwise trend is NA fo this period
                    trend.append(np.nan)


        trend = { 'V_trend_'+ var +'_st_'+ str(wlength): trend} 
        trend = pd.DataFrame(trend)
        
        self.coindata[coin_name] = pd.concat([self.coindata[coin_name],
                                              trend], axis=1)
        
        print("|---| Added shorterm trend (wlength = "
              + str(wlength)
              +") < "+var+" > for: |---| "
              + coin_name)



def add_trend_longterm(self,
                       var,
                       wlength       = "from_config",
                       periodiz_mult = "from_config",
                       ols_minobs    = "from_config"):

    # Input either from config file or specified in arguments
    if wlength == "from_config":
        wlength = self.config["dataloading"]["trend_longterm_windowlength"]
    elif not type(wlength) == int:
        raise TypeError("Input has to be an integer.")
    
    if periodiz_mult == "from_config":    
        periodiz_mult = self.config["dataloading"]["trend_longterm_periodization_multiplier"]
    elif not type(periodiz_mult) == int:
        raise TypeError("Input has to be an integer.")

    if ols_minobs == "from_config":    
        ols_minobs = self.config["dataloading"]["trend_longterm_ols_minobs"]
    elif not type(ols_minobs) == int:
        raise TypeError("Input has to be an integer.")

    if not var in [self.price_var,self.vol_var]:    
        raise TypeError("Input has to be price or volume column.")

    for coin_name in self.coindata.keys():

        if var == self.price_var:
            basevar = self.coindata[coin_name][self.price_var]
        elif var == self.vol_var:
            basevar = self.coindata[coin_name][self.vol_var]

            # Inputs required for longterm trend
        basevar_changes = basevar / basevar.shift(-1) - 1
        basevar_changes.index   = self.coindata[coin_name]["time"]

        # Loop over timeseries to apply rolling functionality (OLS here)
        trend = list()
        for i in range(len(basevar_changes)):
            
            # Determine cut to apply functionality to
            index_from = i
            index_to   = wlength + i
            
            # Extract data for regression
            regressiondata_endog_var = basevar_changes.shift(-1)[index_from:index_to]
            regressiondata_exog_var  = basevar_changes[index_from:index_to]
            regressiondata = pd.concat([regressiondata_endog_var,regressiondata_exog_var],
                                       axis = 1)
            regressiondata.columns = ["basevar_changes","lagged_basevar_changes"]
            # Performance of regression on data extract if sufficient observ.
            cond_nans_data_exog   = regressiondata_exog_var.isna().sum()
            cond_nans_data_endog  = regressiondata_endog_var.isna().sum()
            cond_inf_data_exog    = np.isinf(regressiondata_exog_var).any()
            cond_inf_data_endog   = np.isinf(regressiondata_endog_var).any()
            cond_to_little_observatios = regressiondata.shape[0] < ols_minobs 
            if (cond_nans_data_endog or
                cond_nans_data_exog or
                cond_inf_data_endog or
                cond_inf_data_exog or
                cond_to_little_observatios):
                slope = np.nan
            else:
                slope = sm.ols(formula = "basevar_changes ~ lagged_basevar_changes", 
                               data    = regressiondata,
                               missing = 'drop').fit().params[1]
                
            slope_periodized = slope * periodiz_mult
            trend.append(slope_periodized)
                
        trend = { 'V_trend_'+ var +'_lt_'+ str(wlength): trend} 
        trend = pd.DataFrame(trend)
            
        self.coindata[coin_name] = pd.concat([self.coindata[coin_name],
                                              trend], axis=1)    
        print("|---| Added longterm trend (wlength = "
              + str(wlength)
              +") < "+ var +" > for: |---| "
              + coin_name)


# coin_name = "dai"
# scalingvar = 0.25
# minobs = 0
# wlength = 3
# import numpy as np
# var = "prices"

# for coin_name in d.coindata.keys():
# # The trend variable uses weighted sums of historic price changes.
# # This sum is based on the length of the used time window k. 
# # For calculation we adapt Y steps:
# # 1) Prepare some variables used in the later loop
# # 2) Create a list of tuples for selecting elements of the price vector
# # .. that later used to determine *which* historic prices changes are
# # .. part of the summand
# # 3) A nested loop going through every period and within every period
# # .. trough every tuple to select k summands to include for the trend
# # .. value for the respective period. (Caginalp 2014, p.10)

# # 1) Some preparation
# if var == d.price_var:
#     basevar = d.coindata[coin_name][d.price_var]
# elif var == d.vol_var:
#     basevar = d.coindata[coin_name][d.vol_var]
# else:
#     raise TypeError("This should never trigger.")

# norm_factor = 1/sum([np.exp(scalingvar*i) for i in range(1,wlength+1)])

# # 2) Selection tuples of indeces for historic price to be part of sum per period
# tuple_selections_over_time  = d._make_tuples(windowlength = wlength, series = basevar)

# # 3) Loop to concatenate weighted sums of price changes per period 
# trend = list()
# for tuple_selection_for_period in tuple_selections_over_time:

#     sum_for_period = 0
#     cond_sufficient_obs = len(tuple_selection_for_period) >= minobs

#     if cond_sufficient_obs:
#         for k, tupl in enumerate(tuple_selection_for_period):

#             price_updated = basevar[tupl[0]] #"larger" time if it was timestamp
#             price_anchor  = basevar[tupl[1]] #"smaller" time if it was timestamp
#             weight        = np.exp(-scalingvar*(k+1))# "+1" as enumerate starts with 0

#             if price_anchor == 0:
#                 sum_for_period = np.nan
#                 break

#             sum_for_period += weight * (
#                 (price_updated-price_anchor) / price_anchor
#             )

#         trend.append(norm_factor*sum_for_period)

#     else:
#         # otherwise trend is NA fo rhtis period
#         trend.append(np.nan)


# trend = { 'V_trend_'+ var +'_st_'+ str(wlength): trend} 
# trend = pd.DataFrame(trend)

# d.coindata[coin_name] = pd.concat([d.coindata[coin_name],
#                                       trend], axis=1)

# print("|---| Added shorterm trend (wlength = "
#       + str(wlength)
#       +") < "+var+" > for: |---| "
#       + coin_name)



# sum_for_period = 0
# cond_sufficient_obs = len(tuple_selection_for_period) >= minobs

# for k, tupl in enumerate(tuple_selection_for_period):

#     price_updated = basevar[tupl[0]] #"larger" time if it was timestamp
#     price_anchor  = basevar[tupl[1]] #"smaller" time if it was timestamp
#     weight        = np.exp(-scalingvar*k)

#     if price_anchor == 0:
#         sum_for_period = np.nan
#         break

#     sum_for_period += weight * (
#         (price_updated-price_anchor) / price_anchor
#     )

# trend.append(norm_factor*sum_for_period)



#################################################################################

# coin_name = "dai"
# scalingvar = 0.25
# minobs = 0
# wlength = 31
# import numpy as np
# var = "prices"
# ols_minobs = 20
# import statsmodels.formula.api as sm
# periodiz_mult = 31

# if var == d.price_var:
#     basevar = d.coindata[coin_name][d.price_var]
# elif var == d.vol_var:
#     basevar = d.coindata[coin_name][d.vol_var]

#     # Inputs required for longterm trend
# basevar_changes = basevar / basevar.shift(-1) - 1
# basevar_changes.index   = d.coindata[coin_name]["time"]

# # Loop over timeseries to apply rolling functionality (OLS here)
# trend = list()
# for i in range(len(basevar_changes)):
#     # Determine cut to apply functionality to
#     index_from = i
#     index_to   = wlength + i
#     print("from:{}, to:{}".format(index_from, index_to))
#     # Extract data for regression
#     regressiondata_endog_var = basevar_changes.shift(-1)[index_from:index_to]
#     regressiondata_exog_var  = basevar_changes[index_from:index_to]
#     regressiondata = pd.concat([regressiondata_endog_var,regressiondata_exog_var],
#                                axis = 1)
#     regressiondata.columns = ["basevar_changes","lagged_basevar_changes"]
#     # Performance of regression on data extract if sufficient observ.
#     cond_nans_data_exog   = regressiondata_exog_var.isna().sum()
#     cond_nans_data_endog  = regressiondata_endog_var.isna().sum()
#     cond_inf_data_exog    = np.isinf(regressiondata_exog_var).any()
#     cond_inf_data_endog   = np.isinf(regressiondata_endog_var).any()
#     cond_to_little_observatios = regressiondata.shape[0] < ols_minobs 
#     if (cond_nans_data_endog or
#         cond_nans_data_exog or
#         cond_inf_data_endog or
#         cond_inf_data_exog or
#         cond_to_little_observatios):
#         slope = np.nan
#     else:
#         slope = sm.ols(formula = "basevar_changes ~ lagged_basevar_changes", 
#                        data    = regressiondata,
#                        missing = 'drop').fit().params[1]
#     slope_periodized = slope * periodiz_mult
#     print("S:{}, SP:{}".format(slope, slope_periodized))
#     trend.append(slope_periodized)
