import pandas_gbq as gbq
import re
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
import pymorphy2
from google.oauth2 import service_account
from env import project_id, private_key,credentials, stops

import json
from google.cloud import bigquery
import requests
import pandas as pd
import time 

morph=pymorphy2.MorphAnalyzer()
stemmer=SnowballStemmer('russian')
gbq.context.credentials = credentials
gbq.context.project = project_id

# загрузить посты из определенной группе 
def upload_post_from_vk_group(username,group_id,project_id,credentials):
    token = 'e7a79876e7a79876e7a79876e9e7ce3561ee7a7e7a79876bb0457d3e507797f75821138'
    version = 5.92
    count = 100
    offset = 0
    all_posts = []
    x = 100
    df = pd.DataFrame(columns=['group_id','group_name', 'post_id','post','annotation','keywords'])
    response= requests.get('https://api.vk.com/method/groups.getById',
                            params={
                                'group_id': group_id,
                                'access_token': token,
                                'v': version,
                                
                            }
                            )

    print(response.json())
    try:
        group_name=response.json()['response'][0]['name']
    except:
        return([])
    k=100
    while (k==100):
        start_time = time.time()
        if group_id.isnumeric():
            response = requests.get('https://api.vk.com/method/wall.get',
                                    params={
                                        'access_token': token,
                                        'v': version,
                                        'owner_id': '-'+group_id,
                                        'count': count,
                                        'offset':offset
                                    }
                                    )
        else:
            response = requests.get('https://api.vk.com/method/wall.get',
                                    params={
                                        'access_token': token,
                                        'v': version,
                                        'domain': group_id,
                                        'count': count,
                                        'offset':offset
                                    }
                                    )
        try:
            data = response.json()['response']['items']
        except:
            return ([])
        offset += 100
        k=len(data)
        j=0
        for i in range(k):
            annotation = 'annotation'
            keywords = 'keywords'
            post_id = data[i]['id']
            post = data[i]['text']
            if post!='':
                df.loc[j] = [group_id,group_name,int(post_id), post,annotation,keywords]
                j+=1
        gbq.to_gbq(df,'dataset.vk_storage_'+username, project_id , if_exists = 'append')
        time.sleep(0.1)
        

def delete_row_group_from_user_library(username,group_id, credentials=credentials,project_id=project_id):

    client = bigquery.Client(project=project_id,credentials=credentials)
    
    Query=f'DELETE  FROM dataset.vk_storage_{username} WHERE group_id = \'{group_id}\''
    query_job = client.query(Query)
    return show_all_groups(username,project_id,credentials)

def search_in_user_vk_library(username,word='',mode='post',project_id=project_id,credentials=credentials):
    try:
        if mode=='post_from_group':
            group_name,word=word.split(',')

            word = re.sub("[^а-яА-Яa-zA-Z0-9]", " ", word)
            words = word.lower().split()
            words = [w for w in words if not w in stops]
            words = [stemmer.stem(w) for w in words]
            if words=='':
                return "некорректный ввод"

            Query = f'SELECT * FROM dataset.vk_storage_{username}  WHERE group_name=\'{group_name}\' and (post LIKE \''
            for word in words:
                Query+='%{}'.format(word)
            Query +='%\' or post LIKE \' '
            flag=True
            for word in words:
                if flag==True:
                    Query+='%{}'.format(word.capitalize())
                    flag=False
                else:
                    Query+='%{}'.format(word)
            Query +='%\')'

        word = re.sub("[^а-яА-Яa-zA-Z0-9]", " ", word)
        words = word.lower().split()
        words = [w for w in words if not w in stops]
        words = [stemmer.stem(w) for w in words]
        if words=='':
            return "некорректный ввод"

        if mode=='post':
            Query = f'SELECT * FROM dataset.vk_storage_{username}  WHERE post LIKE \''
            for word in words:
                Query+='%{}'.format(word)
            Query +='%\' or post LIKE \' '
            flag=True
            for word in words:
                if flag==True:
                    Query+='%{}'.format(word.capitalize())
                    flag=False
                else:
                    Query+='%{}'.format(word)
            Query +='%\''

        print(Query)
        df = gbq.read_gbq(Query, project_id, credentials=credentials)

        result = df.values.tolist()

        return (result)
    except:
        return []

def show_user_library(username,project_id,credentials):
    Query = f'SELECT author,title FROM dataset.{username}'
    try:
        df = gbq.read_gbq(Query, project_id, credentials=credentials)
        result = df.values.tolist()
        return result 
    except:
        return([])

def delete_row_article_from_user_library(username,author,title,project,credentials):
    print(username)
    print(author)
    print(title)
    client = bigquery.Client(project=project,credentials=credentials)
    Query=f'DELETE  FROM dataset.{username} WHERE author like \'%{author}%\' and title like \'%{title}%\' '
    query_job = client.query(Query)
    return show_user_library(username,project,credentials)

def show_all_groups(username,project_id,credentials):
    try:
        Query = f'SELECT group_id, group_name FROM dataset.vk_storage_{username} group by group_id, group_name'
        df = gbq.read_gbq(Query, project_id, credentials=credentials)
        return df.values.tolist()
    except:
        return ([])

def update_post_from_vk_group(username,group_id,project_id,credentials):
    last_post_id = data_about_group_for_update(username,group_id,project_id,credentials)[0]
    
    token = 'e7a79876e7a79876e7a79876e9e7ce3561ee7a7e7a79876bb0457d3e507797f75821138'
    version = 5.92
    count = 100
    offset = 0
    all_posts = []
    x = 100
    df = pd.DataFrame(columns=['group_id','group_name', 'post_id','post','annotation','keywords'])
    response= requests.get('https://api.vk.com/method/groups.getById',
                            params={
                                'group_id': group_id,
                                'access_token': token,
                                'v': version,
                                
                            }
                            )

    group_name=response.json()['response'][0]['name']
    k=100
    while (k==100):
        start_time = time.time()
        if group_id.isnumeric():
            response = requests.get('https://api.vk.com/method/wall.get',
                                    params={
                                        'access_token': token,
                                        'v': version,
                                        'owner_id': '-'+group_id,
                                        'count': count,
                                        'offset':offset
                                    }
                                    )
        else:
            response = requests.get('https://api.vk.com/method/wall.get',
                                    params={
                                        'access_token': token,
                                        'v': version,
                                        'domain': group_id,
                                        'count': count,
                                        'offset':offset
                                    }
                                    )
        data = response.json()['response']['items']
        
        k=len(data)
        offset += 100
        j=0
        for i in range(len(data)):
            annotation = 'annotation'
            keywords = 'keywords'
            post_id = data[i]['id']
            post = data[i]['text']
            if post!='' and int(post_id)!=last_post_id:
                df.loc[j] = [group_id,group_name,int(post_id), post,annotation,keywords]
                j+=1
            elif int(post_id)==last_post_id:
                break
            
        
        if len(df)!=0:
            gbq.to_gbq(df,'dataset.vk_storage_'+username, project_id , if_exists = 'append')
        time.sleep(0.1)


def data_about_group_for_update(username,group_id,project_id,credentials):
    
    Query = f'SELECT group_id,MAX(CAST(post_id AS integer)) as last FROM dataset.vk_storage_{username} where group_id=\'{group_id}\' group by group_id'
    df = gbq.read_gbq(Query, project_id, credentials=credentials)
    result = df['last'].values.tolist()
    
    return  result
