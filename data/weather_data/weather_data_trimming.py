import pandas as pd
import numpy as np

def rename_cols(df):
    df = df.rename(columns={"Precipitation amount": "rainfall_mm", "Snow depth": "snow_depth_cm", "Air temperature": "air_temp", 
     "Maximum temperature": "max_temp", "Minimum temperature": "min_temp", "Ground minimum temperature": "min_ground_temp"})
    cols = ['city','rainfall_mm', 'snow_depth_cm', 'air_temp', 'max_temp', 'min_temp', 'min_ground_temp']
    df = df[cols]

    return df

def merge_and_replace(df, dfh):
    # This functions makes a union of the daily and hourly observations and replaces some values
    merged = pd.concat([df, dfh])
    merged2 = merged.mask(merged == "-", np.nan)
    merged2[["rainfall_mm", "snow_depth_cm", "air_temp", "max_temp", "min_temp", "min_ground_temp"]] = merged2[["rainfall_mm", "snow_depth_cm", "air_temp", "max_temp", "min_temp", "min_ground_temp"]].astype('float64')
    merged2 = merged2[["city","rainfall_mm", "snow_depth_cm", "air_temp", "max_temp", "min_temp", "min_ground_temp"]].interpolate(axis=0)
    merge3 = merged2
    merge3["rainfall_mm"] = merge3["rainfall_mm"].where(merge3["rainfall_mm"] >= 0, 0)
    merge3["snow_depth_cm"] = merge3["snow_depth_cm"].mask(merge3["snow_depth_cm"] == -1, 0)
    return merge3


 
