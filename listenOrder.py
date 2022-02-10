from ast import While
from numpy import record
import utility
import math
import datetime


def storeEvent(event,slug,total_supply):
    asset = event['asset']
    if not asset:
        return
    token_id = asset['token_id']
    record_find = db[slug].find_one({ "token_id": token_id })
    if not record_find:
        print('no find')
        auction_type = event['auction_type']

        if auction_type == 'english':
            return 

        current_price = str(float(event['ending_price']) /  math.pow(10,18))
        listing_time = event['listing_time']

        record_find = {
            'token_id': asset['token_id'],
            'traits': [],
            'score': 0.0,
            'current_price': current_price,
            'listing_time': listing_time,
            'is_notice': False
        }

        db[slug].insert_one(record_find)
        
    else:
        record_find_list_time = record_find['listing_time']
        listing_time = event['listing_time']

        current_price = str(float(event['ending_price']) /  math.pow(10,18))
        newvalues = { "$set": { 
                "current_price": current_price, 
                "listing_time":listing_time,
                "is_notice": False
            } 
        }
        db[slug].update_one({ "token_id": token_id }, newvalues)
        
if __name__ == '__main__':
    slug =utility.listenSlug()
    collection_detail = utility.dataOfRetryUntilResponseOk(utility.getCollectionResponse(slug)) 
    
    contract_address = collection_detail['collection']['primary_asset_contracts'][0]['address']
    total_supply = int(collection_detail['collection']['stats']['total_supply'])

    db = utility.initDB()
    while True:
        now =  datetime.datetime.utcnow().isoformat()

        events = utility.getCreatedOrderEvent(contract_address,now)

        try:
            asset_events = events['asset_events']
        except KeyError:
            asset_events = []

        for event in asset_events:
            storeEvent(event,slug,total_supply)

        print("store event ok")
        utility.delay(3)