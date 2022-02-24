import requests
import numpy as np
from funcy import pluck
from random_user_agent.user_agent import UserAgent
import math
from dotenv import load_dotenv
import os
import datetime
import pause
import pymongo
import json
import random


DEFAUL_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36'
load_dotenv()

def getAssets(contract ,offset = 0,params = {},user_agent=DEFAUL_USER_AGENT):
    url = 'https://api.opensea.io/api/v1/assets'
    print('url = {}'.format(url))
    header = { 
        "User-Agent": user_agent,
        "X-API-KEY": os.getenv('X-API-KEY'),
    }
    myparams={
        "asset_contract_address":contract,
        "limit":50,
        "offset":offset,
    }
    myparams.update(params)
    user_agent_rotator = UserAgent(limit=100)
    try:
        status_code = ""
        while status_code != 200:
            
            res = requests.get(url=url, params=myparams,headers=header)
            status_code = res.status_code
            print("get assets status code = {}".format(res.status_code))
            data = res.json()
            if status_code != 200:
                delay(5)
                header['User-Agent'] = user_agent_rotator.get_random_user_agent()

    except Exception as ex:
        print('get assets error message = {}'.format(ex))

        data = []

    return data

def getAssetsResponse(contract , params = {}):
    url = 'https://api.opensea.io/api/v1/assets'
    header = { 
        "X-API-KEY": os.getenv('X-API-KEY'),
    }
    myparams={
        "asset_contract_address":contract,
        "limit":50,
    }
    myparams.update(params)
    try:
        res = requests.get(url=url, params=myparams,headers=header)
    except Exception as ex:
        print('get assets Response error message = {}'.format(ex))
  
        res = None

    return res

def getCollectionAssets(contract_address):
    result =[]

    is_get_data = True
    while is_get_data:
        data = getAssets(contract_address,len(result))

        try:
            tmp = data['assets']
            result = result + data['assets']
    
            if not data['assets']:
                is_get_data = False

        except KeyError:
            is_get_data = False

    return result

def getCollectionSoldOrders(contract_address):
    result = []
    print('start get all assets')
    collection_assets = getCollectionAssets(contract_address)
    print('end get all assets')
    token_ids = list(pluck("token_id", collection_assets))
    np_array = np.array(token_ids)

    index = 0
    user_agent_rotator = UserAgent(limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()

    while index <= len(token_ids):
        token_ids_query = np_array[index:index+30]

        params = {
            'token_ids': token_ids_query,
            'asset_contract_address':contract_address,
            'sale_kind':0,
            'side':1,
            'order_by':"eth_price",
            'order_direction':'asc'
        }

        header = { 
            "X-API-KEY": os.getenv('X-API-KEY'),
            'User-Agent': user_agent
        }
        url = 'https://api.opensea.io/wyvern/v1/orders'

        res = requests.get(url=url, params=params,headers=header)

        if res.status_code == 200:
            data = res.json()
            for order_object in data['orders']:
                token_id = order_object['asset']['token_id']
                base_price = order_object['base_price']
                base_price = int(base_price) /math.pow(10,18)

                result.append((token_id,base_price))
                
        elif res.status_code == 429:
            user_agent = user_agent_rotator.get_random_user_agent()
            print('status 429 change ua to: {}'.format(user_agent))

            continue
        else:
            print(res.status_code)
            content = res.content
            print("response is not 200 content = {}".format(res.content))
        
        index += 30
    result.sort(key=lambda x: x[1], reverse=False)

    return result

def getCancelOrderEvent(contract_address,occurred_after=None):
    url = 'https://api.opensea.io/api/v1/events?asset_contract_address={}&event_type=cancelled&only_opensea=true'.format(contract_address)
    if occurred_after:
        url = url + '&occurred_after={}'.format(occurred_after)
    header = { 
        "X-API-KEY": os.getenv('X-API-KEY'),
        'User-Agent': DEFAUL_USER_AGENT
    }
    try:
        res = requests.get(url=url, headers=header)
        data = res.json()
    except Exception as ex:
        print('get cancel order event error message = {}'.format(ex))

        data = []

    return data

def getCreatedOrderEvent(contract_address,occurred_after=None):
    url = 'https://api.opensea.io/api/v1/events?asset_contract_address={}&event_type=created&only_opensea=true'.format(contract_address)
    if occurred_after:
        url = url + '&occurred_after={}'.format(occurred_after)
    header = { 
        "X-API-KEY": os.getenv('X-API-KEY'),
        'User-Agent': DEFAUL_USER_AGENT
    }
    try:
        status_code = ''
        while status_code != 200:
            res = requests.get(url=url, headers=header)
            status_code = res.status_code
            print(status_code)
            data = res.json()
    except Exception as ex:
        print('get creat order event error message = {}'.format(ex))

        data = []
        
    return data

def delay(seconds=0,minutes=0,hours=0):
    now = datetime.datetime.now()
    until_time = now + datetime.timedelta(hours=hours,minutes=minutes,seconds=seconds)
    pause.until(until_time)

def getCollectionResponse(slug):
    try:
        url = 'https://api.opensea.io/api/v1/collection/{}'.format(slug)
        header = { 
            "X-API-KEY": os.getenv('X-API-KEY'),
        }   
        res = requests.get(url=url, headers=header)
    except Exception as ex:
        print('get Collection Response error message = {}'.format(ex))
        res = None

    return res

def getAssetsRarityScore(asset_trait_object,collection_items_count):
    score = 0.0
    if len(asset_trait_object) <=1 :
        return score
    for trait in asset_trait_object:
        if trait['trait_type'] == "Status":
            return 0.0

        if trait['trait_count'] == 0 :
            break
        value = 1 / (trait['trait_count']/int(collection_items_count))
        score += value
    
    return score

def getListingPrice(asset):
    sell_orders = asset["sell_orders"]

    if sell_orders == None :
        return "0"
    
    closing_extendable = sell_orders[0]['closing_extendable']

    if closing_extendable == True:
        return "0"

    current_price = float(sell_orders[0]['current_price']) /  math.pow(10,18)


    return str(current_price)

def initDB():
    client = pymongo.MongoClient("mongodb://mongodb:27017/")
    db = client.myCollection

    return db

def notify(message):
    body = {
        "chat_id" : -621665809,
        "text" : message,
        "parse_mode" : "markdown"
    }

    url = 'https://api.telegram.org/bot5004774702:AAG1s0Ay_VwrNVbGJuuLoHrZZmBXH0Yp-fo/sendMessage'
    header = { 
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    }   
    res = requests.get(url=url, headers=header,data=json.dumps(body))
    data = res.json()

    print(data)

def listenSlug():
    return os.getenv('LISTEN_PROJECT')

def dataOfRetryUntilResponseOk(request_function):
    status_code = None
    while status_code != 200:
        response = request_function
        status_code = response.status_code

        if status_code == 429:
            delay(5)
        
    return response.json()

def getJaccardDistance(traits,diff_traits):
    sum_object_array = traits + diff_traits

    # same = set([x['value'] for x in sum_object_array if sum_object_array.count(x) > 1])
    seen = set()
    seen_add = seen.add
    same = set(x['value'] for x in sum_object_array if x['value'] in seen or seen_add(x['value']) )

    unique = set([y['value'] for y in sum_object_array])
    
    return 1 - (len(same) / len(unique))



    traits_pluck = [x["value"] for x in traits]
    #['Cowboy Hat', 'Ape', '1 attributes']

    diff_traits_pluck = [x["value"] for x in diff_traits]
    #['Fedora', 'Ape', '1 attributes']

    both = traits_pluck + diff_traits_pluck
    #['Cowboy Hat', 'Ape', '1 attributes', 'Fedora', 'Ape', '1 attributes']

    same = list(set([x for x in both if both.count(x) > 1]))
    #['Ape', '1 attributes']

    unique = list(set(traits_pluck + diff_traits_pluck))
    #['Ape', 'Cowboy Hat', '1 attributes', 'Fedora']
    
    return 1 - (len(same) / len(unique))
    
def getAbi(address):
    try:
        url = 'https://api.etherscan.io/api'
        myparams={
            "module":'contract',
            "action":'getabi',
            "address":address,
            "apikey":os.getenv('ETHERSCAN_API_KEY')
        }
        res = requests.get(url=url,params=myparams)
    except Exception as ex:
        print('getABI error message = {}'.format(ex))
        res = None

    return res
