#!/usr/bin/env python
# coding: utf-8


import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import warnings
warnings.filterwarnings("ignore")


load_dotenv()
air_pollution_key = os.getenv("air_pollution_API_key")


# functions for race dates

def racedates(season):
    
    """function gives all races for the season and consists of date, location and coordinates"""
    
    races = dict()
    url = f"http://ergast.com/api/f1/{season}.json"
    data = requests.get(url).json()
    number_of_races = int(len(data["MRData"]["RaceTable"]["Races"]))
    for j in range(number_of_races):
        dt = data["MRData"]["RaceTable"]["Races"][j]["date"], data["MRData"]["RaceTable"]["Races"][j]["time"]
        dt2 = " ".join(dt)
        dt3 = pd.to_datetime(dt2)      
        #key = dt3.tz_localize(None)
        key = dt3
        city = data["MRData"]["RaceTable"]["Races"][j]["Circuit"]["Location"]["locality"]
        lat = data["MRData"]["RaceTable"]["Races"][j]["Circuit"]["Location"]["lat"]
        long = data["MRData"]["RaceTable"]["Races"][j]["Circuit"]["Location"]["long"]
        races[key] = [city, lat, long]
    return races



# functions for pollution data

def get_season(start, end):
    
    """ get all files for the season in one file, +/- 7d of race. start/end are indices from all_races df"""
    
    df = single_pollution(start)
    for i in range(start+1, end):
        df2 = single_pollution(i)
        if df2 is not None:
            df = pd.merge(df, df2, on="hours")
    return df


def single_pollution(i):
    
    """ get pollution data """
    
    city_lat = all_races.iloc[i]["lat"]
    city_long = all_races.iloc[i]["long"]
    start = int(all_races.iloc[i]["start"])
    end = int(all_races.iloc[i]["end"])
    url2 = f"http://api.openweathermap.org/data/2.5/air_pollution/history?lat={city_lat}&lon={city_long}&start={start}&end={end}&appid={air_pollution_key}"
    response = requests.get(url2)
    df = response.json()
    pollution = dict()
    for k in range(len(df["list"])):
        dt = df["list"][k]["dt"]
        pollution[datetime.utcfromtimestamp(dt).strftime('%Y-%m-%d %H:%M:%S')] = df["list"][k]["components"]["pm2_5"]
    df2 = pd.DataFrame(pollution.items())
    if len(df2) != 337:
        return
    df2 = df2.rename(columns={0: "date", 1: all_races.iloc[i]["location"]})
    hours_list = list()
    for i in range(-169, 168):
        hours_list.append(i)
    df2["hours"] = hours_list
    df2 = df2.set_index("hours")
    df2 = df2.drop(columns="date")
    return df2


def get_whole_year(lat, long, start, end):
    
    url = f"http://api.openweathermap.org/data/2.5/air_pollution/history?lat={lat}&lon={long}&start={start}&end={end}&appid={air_pollution_key}"

    response = requests.get(url)
    df = response.json()

    race_dict = dict()
    for i in range(len(df["list"])):
        date = df["list"][i]["dt"]
        pm = df["list"][i]["components"]["pm2_5"]
        dt = df["list"][i]["dt"]
        race_dict[datetime.utcfromtimestamp(dt).strftime('%Y-%m-%d %H:%M:%S')] = pm
    df2 = pd.DataFrame(race_dict.items())
    df2 = df2.rename(columns={0: "date", 1: "pm"})
    return df2


