import requests
import json
import numpy as np
import math
from random_user_agent.user_agent import UserAgent
import utility
import time
from datetime import datetime

def soldOrdersRemoveCancel(contract_address,soldOrders,occurred_after):
    cancel_order_event = utility.getCancelOrderEvent(contract_address,now_time)
    
    try:
        for event in cancel_order_event['asset_events']:
            token_id = event['asset']['token_id'] 
            total_price = event['total_price']
            total_price = int(total_price) /math.pow(10,18)

            try:
                soldOrders.remove((token_id, total_price))
            except:
                pass
    except KeyError:
        pass

    return soldOrders

def soldOrdersCreated(contract_address,soldOrders,occurred_after):
    created_order_event = utility.getCreatedOrderEvent(contract_address,now_time)
    
    try:
        for event in created_order_event['asset_events']:
            token_id = event['asset']['token_id'] 
            ending_price = event['ending_price']
            ending_price = int(ending_price) /math.pow(10,18)
            
            if [item for item in soldOrders if item[0] == token_id and item[1] == ending_price]:
                print('exist')
            else:
                soldOrders.append((token_id,ending_price))
    except KeyError:
        pass
    
    soldOrders.sort(key=lambda x: x[1], reverse=False)

    return soldOrders

def canFlipItem(soldOrders):
    result = []
    if len(soldOrders) < 5:
        return []
    average_count = 4
    total_price = 0
    for item in soldOrders[1:average_count+1]:
        total_price += item[1]
    average_price = total_price/average_count

    if soldOrders[0][1] < average_price*0.69:
        result.append((soldOrders[0][0],soldOrders[0][1]))
    
    return result

def notify(contract_address,can_flip_items):
    body = {
        "chat_id" : -790427094,
        "text" : "[link](https://opensea.io/assets/{}/{})".format(contract_address,can_flip_items[0][0]),
        "parse_mode" : "markdown"
    }

    url = 'https://api.telegram.org/bot5277878862:AAGh-AfBwn35qBomaV0OoH3B9bxDvWwYnDs/sendMessage'
    header = { 
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    }   
    res = requests.get(url=url, headers=header,data=json.dumps(body))
    data = res.json()

if __name__ == '__main__':
    contract_address = '0x90cfce78f5ed32f9490fd265d16c77a8b5320bd4'

    now_time = datetime.utcnow()
    now_time = now_time.strftime("%Y-%m-%dT%H:%M:%S")

    soldOrders = utility.getCollectionSoldOrders(contract_address)
    # soldOrders = [('683', 12.2), ('10', 12.4), ('434', 11.0), ('37', 12.89), ('766', 12.9), ('747', 13.5), ('238', 13.5), ('10', 13.8), ('206', 14.5), ('595', 14.6), ('64', 16.4), ('595', 17.0), ('763', 17.5), ('595', 18.5), ('524', 19.99), ('37', 21.99), ('692', 22.0), ('448', 22.0), ('289', 22.0), ('508', 22.22), ('595', 22.5), ('524', 22.5), ('37', 22.5), ('201', 22.5), ('629', 23.0), ('397', 23.0), ('524', 23.5), ('37', 23.5), ('720', 25.0), ('559', 25.0), ('723', 25.2), ('532', 25.99), ('598', 26.0), ('720', 26.5), ('663', 27.0), ('683', 27.5), ('765', 30.0), ('595', 30.0), ('440', 30.0), ('115', 30.0), ('64', 30.9), ('486', 38.0), ('130', 42.69), ('454', 49.0), ('581', 49.9), ('541', 69.042), ('301', 88.0), ('191', 88.88), ('403', 99.0), ('689', 100.0), ('355', 100.0), ('152', 100.0), ('734', 734.0), ('268', 900.0), ('9', 9999.0)]
    
    while True:
        soldOrders = soldOrdersRemoveCancel(contract_address,soldOrders,now_time)
        soldOrders = soldOrdersCreated(contract_address,soldOrders,now_time)
    
        can_flip_items = canFlipItem(soldOrders)

        if can_flip_items:
            notify(contract_address,can_flip_items)
        
        now_time = datetime.utcnow()
        now_time = now_time.strftime("%Y-%m-%dT%H:%M:%S")

        utility.delay(30)