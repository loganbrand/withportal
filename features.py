#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 09:34:08 2017

@author: Wiebke Toussaint

Answer query script: This script contains functions to query and manipulate DLR survey answer sets. It references datasets that must be stored in a /data/tables subdirectory in the parent directory.

"""

import numpy as np
import pandas as pd
import os
import feather
import ckanapi

from support import table_dir

def loadTable(name, query=None, columns=None):
    """
    This function loads all feather tables in filepath into workspace.
    
    """
    dir_path = os.path.join(table_dir, 'feather')
    
    try:
        file = os.path.join(dir_path, name +'.feather')
        d = feather.read_dataframe(file)
        if columns is None:
            table = d
        else:
            table = d[columns]
            
    except:
        #fetch tables from energydata.uct.ac.za
        ckan = ckanapi.RemoteCKAN('http://energydata.uct.ac.za/', get_only=True)
        resources = ckan.action.package_show(id='dlr-database-tables-94-14')        
        for i in range(0, len(resources['resources'])):
            if resources['resources'][i]['name'] == name:
                print('... fetching ' + name + ' from energydata.uct.ac.za')
                r_id = resources['resources'][i]['id']
                d = ckan.action.datastore_search(resource_id=r_id, q=query, fields=columns, limit=1000000)['records']
                table = pd.DataFrame(d)
                table = table.iloc[:,:-1]
            else:
                pass
    try: 
        return table

    except UnboundLocalError:
        return('Could not find table with name '+name)    

def loadID():
    """
    This function subsets Answer or Profile IDs by year. Tables variable can be constructred with loadTables() function. Year input can be number or string. id_name is AnswerID or ProfileID. 
    """
    groups = loadTable('groups')
    links = loadTable('links')
    profiles = loadTable('profiles')
    
#    a_id = links[(links.GroupID != 0) & (links['AnswerID'] != 0)].drop(columns=['ConsumerID','lock','ProfileID'])
    p_id = links[(links.GroupID != 0) & (links['ProfileID'] != 0)].drop(columns=['ConsumerID','lock','AnswerID'])
    profile_meta = profiles.merge(p_id, how='left', left_on='ProfileId', right_on='ProfileID').drop(columns=['ProfileId','lock'])

    ap = links[links.GroupID==0].drop(columns=['ConsumerID','lock','GroupID'])
    x = profile_meta.merge(ap, how='outer', on = 'ProfileID')    
    join = x.merge(groups, on='GroupID', how='left')

    #Wrangling data into right format    
    all_ids = join[join['Survey'] != 'Namibia'] # take Namibia out
    all_ids = all_ids.dropna(subset=['GroupID','Year'])
    all_ids.Year = all_ids.Year.astype(int)
    all_ids.GroupID = all_ids.GroupID.astype(int)
    all_ids.AnswerID.fillna(0, inplace=True)
    all_ids.AnswerID = all_ids.AnswerID.astype(int)
    all_ids.ProfileID = all_ids.ProfileID.astype(int)
        
    return all_ids

def loadAnswers():
    """
    This function returns all answer IDs and their question responses for a selected data type. If dtype is None, answer IDs and their corresponding questionaire IDs are returned instead.
    
    """
    answer_meta = loadTable('answers', columns=['AnswerID', 'QuestionaireID'])

    blob = loadTable('answers_blob_anonymised').drop(labels='lock', axis=1)
    blob = blob.merge(answer_meta, how='left', on='AnswerID')
    blob.fillna(np.nan, inplace = True)
    
    char = loadTable('answers_char_anonymised').drop(labels='lock', axis=1)
    char = char.merge(answer_meta, how='left', on='AnswerID')
    char.fillna(np.nan, inplace = True)

    num = loadTable('answers_number_anonymised').drop(labels='lock', axis=1)
    num = num.merge(answer_meta, how='left', on='AnswerID')
    num.fillna(np.nan, inplace = True)

    return {'blob':blob, 'char':char, 'num':num}

def searchQuestions(search = None):
    """
    Searches questions for a search term, taking questionaire ID and question data type (num, blob, char) as input. 
    A single search term can be specified as a string, or a list of search terms as list.
    
    """       
    questions = loadTable('questions').drop(labels='lock', axis=1)
    questions.Datatype = questions.Datatype.astype('category')
    questions.Datatype.cat.categories = ['blob','char','num']
        
    if search is None:
        searchterm = ''
    else:
        searchterm = search.lower().replace(' ', '+')

    result = questions.loc[questions.Question.str.lower().str.contains(searchterm), ['Question', 'Datatype','QuestionaireID', 'ColumnNo']]
    return result

def searchAnswers(search):
    """
    This function returns the answers IDs and responses for a list of search terms
    
    """
    answers = loadAnswers()

    questions = searchQuestions(search) #get column numbers for query
    
    result = pd.DataFrame(columns=['AnswerID','QuestionaireID'])
    for dt in questions.Datatype.unique():
        ans = answers[dt]
        for i in questions.QuestionaireID.unique():            
            select = questions.loc[(questions.Datatype == dt)&(questions.QuestionaireID==i)]            
            fetchcolumns=['AnswerID'] + ['QuestionaireID'] + list(select.ColumnNo.astype(str))
            newcolumns = ['AnswerID'] + ['QuestionaireID'] + list(select.Question.astype(str).str.lower())
            
            df = ans.loc[ans['QuestionaireID']==i,fetchcolumns]           
            df.columns = newcolumns
            
            result = result.merge(df, how='outer')
            
    return result

def buildFeatureFrame(searchlist):
    """
    This function creates a dataframe containing the data for a set of selected features for a given year.
    
    """
    if isinstance(searchlist, list):
        pass
    else:
        searchlist = [searchlist]
    
    result = pd.DataFrame(columns=['AnswerID','QuestionaireID'])        
    for s in searchlist:
        d = searchAnswers(s)
        ans = d[d.QuestionaireID.isin([3,6])]
        ans = ans.dropna(axis=1, how='all')
        
        result = result.merge(ans, how='outer')
        
    return result

def checkAnswer(answerid, features):
    """
    This function returns the survey responses for an individuals answer ID and list of search terms.
    
    """
    links = loadTable('links')
    groupid = links.loc[links['AnswerID']==answerid].reset_index(drop=True).get_value(0, 'GroupID')
    groups = loadTable('groups')
    year = int(groups.loc[groups.GroupID == groupid, 'Year'].reset_index(drop=True)[0])
    
    ans = buildFeatureFrame(features, year)[0].loc[buildFeatureFrame(features, year)[0]['AnswerID']==answerid]
    return ans

def recorderLocations(year = 2014):
    """
    This function returns all survey locations and recorder abbreviations for a given year. Only valid from 2009 onwards.
    
    """
    if year > 2009:
        stryear = str(year)
        groups = loadTable('groups')
        recorderids = loadTable('recorderinstall')
        
        reclocs = groups.merge(recorderids, left_on='GroupID', right_on='GROUP_ID')
        reclocs['recorder_abrv'] = reclocs['RECORDER_ID'].apply(lambda x:x[:3])
        yearlocs = reclocs.loc[reclocs['Year']== stryear,['GroupID','LocName','recorder_abrv']].drop_duplicates()
        
        locations = yearlocs.sort_values('LocName')
        return locations 
    
    else:
        print('Recorder locations can only be returned for years after 2009.')

def lang(code = None):
    """
    This function returns the language categories.
    
    """
    language = dict(zip(searchAnswers(qnairid=5)[0].iloc[:,1], searchAnswers(qnairid=5,dtype='char')[0].iloc[:,1]))
    if code is None:
        pass
    else:
        language = language[code]
    return language

def altE(code = None):
    """
    This function returns the alternative fuel categories.
    
    """
    altenergy = dict(zip(searchAnswers(qnairid=8)[0].iloc[:,1], searchAnswers(qnairid=8,dtype='char')[0].iloc[:,1]))
    if code is None:
        pass
    else:
        altenergy = altenergy[code]
    return altenergy
