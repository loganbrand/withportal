#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 12:48:14 2018

@author: saintlyvi
"""

import ckanapi
import pandas as pd
import os
import feather
from pathlib import Path

table_dir = os.path.join('data','table')

def appData():
           
    csv_table = os.path.join(table_dir, 'csv')
    feather_table = os.path.join(table_dir, 'feather')
    os.makedirs(csv_table, exist_ok=True)
    os.makedirs(feather_table, exist_ok=True)
    
    csv_adtd = os.path.join('data', 'aggProfiles', 'csv')
    feather_adtd = os.path.join('data', 'aggProfiles', 'feather')
    os.makedirs(csv_adtd, exist_ok=True)
    os.makedirs(feather_adtd, exist_ok=True)
    
    #fetch tables from energydata.uct.ac.za
    apikey = input('Enter your APIKEY from http://energydata.uct.ac.za/user/YOUR_USERNAME: ')
    ckan = ckanapi.RemoteCKAN('http://energydata.uct.ac.za/', apikey=apikey, get_only=True)

    tables = ckan.action.package_show(id='dlr-database-tables-94-14')        
    for i in range(0, len(tables['resources'])):
            name = tables['resources'][i]['name']
            print('... fetching ' + name + ' from energydata.uct.ac.za')
            r_id = tables['resources'][i]['id']
            d = ckan.action.datastore_search(resource_id=r_id)['records']
            table = pd.DataFrame(d)
            table = table.iloc[:,:-1]
            
            feather.write_dataframe(table, os.path.join(feather_table, name + '.feather'))
            table.to_csv(os.path.join(csv_table, name + '.csv'), index=False)
    
    profiles = ckan.action.package_show(id='dlr-average-day-type-demand-profiles')        
    for i in range(0, len(profiles['resources'])):
            name = profiles['resources'][i]['name']
            print('... fetching ' + profiles['resources'][i]['name'] + ' from energydata.uct.ac.za')
            r_id = profiles['resources'][i]['id']
            d = ckan.action.datastore_search(resource_id=r_id)['records']
            adtd = pd.DataFrame(d)
            #write profiles to disk                
            feather.write_dataframe(adtd, os.path.join(feather_adtd, name + '.feather'))
            adtd.to_csv(os.path.join(csv_adtd, name + '.csv'), index=False)

    print('Your app is starting now. Go to 127.0.0.0:8050')
    return

def readAggProfiles(year):
    """
    This function fetches aggregate load profile data from disk. aggfunc can be one of pp, aggpp_M, aMd, adtd
    """
    path = os.path.join('data', 'aggProfiles', 'feather')
    
    if os.listdir(path) == []:
        appData()
    
    else:         
        path = Path(path)        
        for child in path.iterdir():
            n = child.name
            nu = n.split('.')[0].split('_')[-1]
            if int(nu)==year:
                df = feather.read_dataframe(str(child))
                return df     

def appProfiles():
    
    data = pd.DataFrame()
    
    for y in range(1994, 2015):
        d = readAggProfiles(y)
        data = data.append(d)