import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None  # default='warn'

def get_features(df, cities):

    appended_data = []
    for c in cities:
        dff = df.loc[df['city'] == c]
        dff["rain_sum_7d"] = dff["rainfall_mm"].replace(-1, 0).shift(1).rolling(7).sum().round(2)
        dff["snow_depth_cm"] = dff["snow_depth_cm"].replace(0, np.nan).ffill()
        dff["snow_var_7d"] = dff["snow_depth_cm"].replace(-1, 0).shift(1).rolling(7).var().round(2)
        dff["min_temp_2d"] = dff["min_temp"].shift(1).rolling(2).min().round(2)
        dff["max_temp_2d"] = dff["max_temp"].shift(1).rolling(2).max().round(2)
        dff["is_neg"] = dff["min_temp"]<0
        dff["is_neg"] = dff["is_neg"].astype(int).shift(1)
        dff["neg_rate_7d"] = dff["is_neg"].shift(1).rolling(7).mean().round(2)
        dff = dff.bfill()
        features = dff.drop(columns=['rainfall_mm', 'snow_depth_cm', 'air_temp', 'max_temp', 'min_temp', 'min_ground_temp', 'is_neg']).sort_index(axis=0, ascending=False)
        features = features.head(1).fillna(0)
        appended_data.append(features)
    
    all_features = pd.concat(appended_data)

    return all_features

