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

from support import table_dir

def loadTable(name, query=None, columns=None):
    """
    This function loads all feather tables in filepath into workspace.
    
    """
    dir_path = os.path.join(table_dir, 'feather')
    
    file = os.path.join(dir_path, name +'.feather')
    d = feather.read_dataframe(file)
    if columns is None:
        table = d
    else:
        table = d[columns]
            
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
        searchterm = search.replace(' ', '+')

    trantab = str.maketrans({'(':'', ')':'', ' ':'', '/':''})
    
    result = questions.loc[questions.Question.str.translate(trantab).str.contains(searchterm, case=False), ['Question', 'Datatype','QuestionaireID', 'ColumnNo']]
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

def buildFeatureFrame(searchlist, year=None, cols=None):
    """
    This function creates a dataframe containing the data for a set of selected features for a given year.
    
    """
    if isinstance(searchlist, list):
        pass
    else:
        searchlist = [searchlist]
        
    if cols is None:
        search = dict(zip(searchlist, searchlist))
    else:
        search = dict(zip(searchlist, cols))
    
    #filter AnswerIDs by year          
    ids = loadID()
    if year is None:
        sub_ids = ids[ids.AnswerID!=0]
    else:
        sub_ids = ids[(ids.AnswerID!=0)&(ids.Year==year)]
    
    #generate feature frame
    result = pd.DataFrame(columns=['AnswerID','QuestionaireID'])        
    for s in search.keys():
        d = searchAnswers(s)
        ans = d[(d.AnswerID.isin(sub_ids.AnswerID)) & (d.QuestionaireID < 10)] # remove non-domestic results 
        ans = ans.dropna(axis=1, how='all')
    #set feature frame column names
        if len(ans.columns[2:])==1:
            ans.columns = ['AnswerID','QuestionaireID'] + [search.get(s)]        

        try:    
            result = result.merge(ans, how='outer')
        except Exception:
            pass
                          
    return result

def socio_demographics(appliances=None, other_socios=None):
    
    if appliances is None:
        appliances = []
    if other_socios is None:
        other_socios = []
    features6 = ['years','monthly income'] + appliances + other_socios
    features3 = ['electricity','deductions'] + ['{}Number'.format(i) for i in appliances] + other_socios     
    cols = ['years_electrified','monthly_income'] + [i.replace(' ','_') for i in appliances] + [i.replace(' ','_') for i in other_socios]

    ff = pd.DataFrame(columns= ['AnswerID','QuestionaireID'] + cols)
    for year in range(1994, 2000):
        try:
            ff = ff.append(buildFeatureFrame(features6, year, cols)) #generate feature frame for years pre 1999
        except Exception:
            print(year)
            pass
        
    for year in range(2000, 2015):
        try:
            ff = ff.append(buildFeatureFrame(features3, year, cols)) #generate feature frame for years post 1999
        except Exception:
            pass                
    ff = ff[['AnswerID','QuestionaireID'] + cols]
    
    return ff

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
