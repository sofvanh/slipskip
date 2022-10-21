import pandas as pd
import numpy as np

def get_features(df):

    df["rain_sum_7d"] = df["rainfall_mm"].replace(-1, 0).shift(1).rolling(7).sum().round(2)
    df["snow_depth_cm"] = df["snow_depth_cm"].replace(0, np.nan).ffill()
    df["snow_var_7d"] = df["snow_depth_cm"].replace(-1, 0).shift(1).rolling(7).var().round(2)
    df["min_temp_2d"] = df["min_temp"].shift(1).rolling(2).min().round(2)
    df["max_temp_2d"] = df["min_temp"].shift(1).rolling(2).max().round(2)
    df["is_neg"] = df["min_temp"]<0
    df["is_neg"] = df["is_neg"].astype(int).shift(1)
    df["neg_rate_7d"] = df["is_neg"].shift(1).rolling(7).mean().round(2)
    df = df.bfill()
    features = df.drop(columns=['rainfall_mm', 'snow_depth_cm', 'air_temp', 'max_temp',
        'min_temp', 'min_ground_temp', 'is_neg'])
    
    return features

