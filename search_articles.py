import re
from nltk.stem.snowball import SnowballStemmer
import pymorphy2

from env import project_id, private_key,credentials, stops

import json
from google.cloud import bigquery
from pandas.io import gbq

import pandas as pd
morph=pymorphy2.MorphAnalyzer()

stemmer=SnowballStemmer('russian')

def search_user_library(username,q='',mode='title'):
    try:
        q = re.sub("[^а-яА-Яa-zA-Z0-9]", " ", q)
        q = q.lower()
        words=q.split()
        words = [w for w in words if not w in stops]
        words = [stemmer.stem(w) for w in words]
        if words=='':
            return "некорректный ввод"

        if mode=='author':
            Query = 'SELECT * FROM dataset.'+username+' WHERE AUTHOR LIKE \''
            for word in words:
                Query+='%{}'.format(word)
            Query += '%\''

            print(1,Query)
            df = gbq.read_gbq(Query, project_id, credentials=credentials)
            print(df.values.tolist())

            if df.values.tolist()==[]:
                print(2)
                Query = 'SELECT * FROM dataset.'+username+' WHERE AUTHOR LIKE \'%{}%\''.format(q)
                print(Query)
                df = gbq.read_gbq(Query, project_id, credentials=credentials)
                print(df.values.tolist())
                if df.values.tolist()==[]:
                    print(3)
                    Query = 'SELECT * FROM dataset.'+username+' WHERE AUTHOR LIKE \'%{}%\''.format(q.capitalize())
                    print(df.values.tolist())
                    df = gbq.read_gbq(Query, project_id, credentials=credentials)

        if mode=='title':
    #         words = [morph.parse(w)[0].normal_form for w in words]
            Query = 'SELECT * FROM dataset.'+username+' WHERE TITLE LIKE \''
            for word in words:
                Query+='%{}'.format(word)
            Query += '%\''
            print(Query)
            df = gbq.read_gbq(Query, project_id, credentials=credentials)
            print(df.values.tolist())
            if df.values.tolist()==[]:
                Query = 'SELECT * FROM dataset.'+username+' WHERE TITLE LIKE \'%{}%\''.format(q)
                print(Query)
                df = gbq.read_gbq(Query, project_id, credentials=credentials)

        if mode=='kws':
    #         words = [morph.parse(w)[0].normal_form for w in words]
            Query = 'SELECT * FROM dataset.'+username+' WHERE KEYWORDS LIKE \''
            for word in words:
                Query+='%{}'.format(word)
            Query += '%\''
            print(Query)
            df = gbq.read_gbq(Query, project_id, credentials=credentials)
            print(df.values.tolist())
            if df.values.tolist()==[]:
                Query = 'SELECT * FROM dataset.'+username+' WHERE KEYWORDS LIKE \'%{}%\''.format(q)
                print(Query)
                df = gbq.read_gbq(Query, project_id, credentials=credentials)
        result = df.values.tolist()
        if result==[]:
            return result
        else:
            return result
    except:
        return []


stemmer=SnowballStemmer('russian')

def search(q='',mode='title'):
    print(mode)
    try:
        q = re.sub("[^а-яА-Яa-zA-Z0-9]", " ", q)
        q = q.lower()
        words=q.split()
        words = [w for w in words if not w in stops]
        words = [stemmer.stem(w) for w in words]
        if words=='':
            return "некорректный ввод"

        if mode=='author':
            Query = 'SELECT * FROM dataset.search_rsl_ru WHERE AUTHOR LIKE \''
            for word in words:
                Query+='%{}'.format(word)
            Query += '%\''
            print(Query)
            df = gbq.read_gbq(Query, project_id, credentials=credentials)
            print(df.values.tolist())
            if df.values.tolist()==[]:
                Query = 'SELECT * FROM dataset.search_rsl_ru WHERE AUTHOR LIKE \'%{}%\''.format(q)
                print(Query)
                df = gbq.read_gbq(Query, project_id, credentials=credentials)
                if df.values.tolist() == []:
                    Query = 'SELECT * FROM dataset.search_rsl_ru WHERE AUTHOR LIKE \'%{}%\''.format(q.capitalize())
                    print(Query)
                    df = gbq.read_gbq(Query, project_id, credentials=credentials)

        if mode=='title':
    #         words = [morph.parse(w)[0].normal_form for w in words]
            Query = 'SELECT * FROM dataset.search_rsl_ru WHERE TITLE LIKE \''
            for word in words:
                Query+='%{}'.format(word)
            Query += '%\''
            print(Query)
            df = gbq.read_gbq(Query, project_id, credentials=credentials)
            print(df.values.tolist())
            if df.values.tolist()==[]:
                Query = 'SELECT * FROM dataset.search_rsl_ru WHERE TITLE LIKE \'%{}%\''.format(q)
                print(Query)
                df = gbq.read_gbq(Query, project_id, credentials=credentials)

        if mode=='kws':
    #         words = [morph.parse(w)[0].normal_form for w in words]
            Query = 'SELECT * FROM dataset.search_rsl_ru WHERE KEYWORDS LIKE \''
            for word in words:
                Query+='%{}'.format(word)
            Query += '%\''
            print(Query)
            df = gbq.read_gbq(Query, project_id, credentials=credentials)
            print(df.values.tolist())
            if df.values.tolist()==[]:
                Query = 'SELECT * FROM dataset.search_rsl_ru WHERE KEYWORDS LIKE \'%{}%\''.format(q)
                print(Query)
                df = gbq.read_gbq(Query, project_id, credentials=credentials)
        result = df.values.tolist()
        if result==[]:
            return []
        else:
            return result
    except:
        return []
