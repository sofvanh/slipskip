import sys, os
import pandas as pd
import numpy as np
import datetime as dt
from fmiopendata.wfs import download_stored_query
from fmiopendata.utils import read_url
#import xml.etree.ElementTree as ET
from lxml import etree

def enablePrint():
    sys.stdout = sys.__stdout__

def get_places():

    xml = read_url("http://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id=fmi::ef::stations")
    #stree = etree.parse(xml)
    #root = ET.fromstring(xml)
    root = etree.fromstring(xml)
    locations = dict()
    for name in root.findall('.//{http://www.opengis.net/gml/3.2}name'):
        if name.attrib['codeSpace'] == 'http://xml.fmi.fi/namespace/locationcode/name':
            city = name.text.split(' ', 1)[0]
            id = name.getparent().find('.//{http://www.opengis.net/gml/3.2}identifier').text
            try:
                place = name.text.split(' ', 1)[1]
            except:
                place = ''
            if city in locations:
                locations[city].append((place,id))
            else:
                locations[city] = [(place, id)]

    #res = np.empty([1, 2])

    #for c in cities:
    #    x = np.array(locations[c]).reshape(len(locations[c]),1)
    #    y = np.broadcast_to([c], (len(locations[c]),1))
    #    r = np.hstack((x,y))
    #    res = np.vstack((res,r))

    return locations #res[1:,:]

    

def get_daily_obs(cities, places):

    # Retrieve the last 10 days daily observations + todays latest 10h observation
    end_time = dt.datetime.utcnow() - dt.timedelta(days=1)
    start_time = end_time - dt.timedelta(days=10)
    # Convert times to properly formatted strings
    start_time = start_time.isoformat(timespec="seconds") + "Z"
    end_time = end_time.isoformat(timespec="seconds") + "Z"

    df = pd.DataFrame({'city': [],'Precipitation amount' : [], 'Air temperature' : [], 'Snow depth' : [], 'Minimum temperature' : [], 'Maximum temperature' : [], 'Ground minimum temperature' : [],})

    for c in cities:
        plcs = places[c]
        appended_data = []
        for p in plcs:
        # For last 10d we get daily values
            obs = download_stored_query("fmi::observations::weather::daily::multipointcoverage",
                                args=["fmisid=" + p[1],
                                    "starttime=" + start_time,
                                    "endtime=" + end_time])
            df2 = pd.DataFrame.from_dict({(i): obs.data[i][j]
                                for i in obs.data.keys() 
                                for j in obs.data[i].keys()},
                            orient='index')
            df2 = df2.applymap(lambda x: x.get('value'))
            if df2.empty == False and (df2['Air temperature'].isnull().all() == False or df2['Ground minimum temperature'].isnull().all() == False):
                appended_data.append(df2)
        df2 = pd.concat(appended_data)
        df2['city'] = c
        df2.index = df2.index.date
        #df2 = df2.groupby([df2.index]).mean()
        df = pd.concat([df,df2])
    
    df = df.groupby([df.index, "city"]).mean().reset_index(level=1)

    return df

def get_hourly_obs(cities, places, cols):
    # Retrieve the last 10 days daily observations + todays latest 10h observation
    end_time = dt.datetime.utcnow()
    start_time = end_time - dt.timedelta(hours=10)
    # Convert times to properly formatted strings
    start_time = start_time.isoformat(timespec="seconds") + "Z"
    end_time = end_time.isoformat(timespec="seconds") + "Z"

    dfh = pd.DataFrame({'city': [], 'Air temperature' : [], 'Precipitation amount' : [],'Snow depth' : []})

    for c in cities:
        plcs = places[c]
        appended_data = []
        for p in plcs:
        # For last 10h we get all observations and use these to calculate the "daily" observations for today
            obs = download_stored_query("fmi::observations::weather::multipointcoverage",
                                args=["fmisid=" + p[1],
                                    "starttime=" + start_time,
                                    "endtime=" + end_time])
            dfh2 = pd.DataFrame.from_dict({(i): obs.data[i][j]
                                for i in obs.data.keys() 
                                for j in obs.data[i].keys()},
                            orient='index')
            dfh2 = dfh2.applymap(lambda x: x.get('value'))
            # We have to calculate some new columns for these hourly observations
            if dfh2.empty == False:
                dfh2['Minimum temperature'] = dfh2['Air temperature'].min()
                dfh2['Maximum temperature'] = dfh2['Air temperature'].max()
                dfh2['Air temperature'] = dfh2['Air temperature'].mean()
                dfh2['Ground minimum temperature'] = dfh2['Minimum temperature']
                dfh2['Precipitation amount'] = dfh2['Precipitation amount'].sum()
            # Let's take only last calculated value as daily value for station
            dfh2 = dfh2.sort_index(axis=0, ascending=False).head(1)
            if dfh2.empty == False and dfh2['Air temperature'].isnull().all() == False:
                appended_data.append(dfh2)
        dfh2 = pd.concat(appended_data)
        dfh2['city'] = c
        dfh2.index = dfh2.index.date
        dfh2 = dfh2[cols]
        dfh = pd.concat([dfh,dfh2])
    
    # Let's take average of station for that city
    dfh = dfh.groupby([dfh.index, "city"]).mean().reset_index(level=1)
    
    return dfh

