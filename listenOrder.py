from ast import While
from numpy import record
import utility
import math

def storeEvent(event,slug,total_supply):
    asset = event['asset']
    if not asset:
        return
    token_id = asset['token_id']
    record_find = db[slug].find_one({ "token_id": token_id })
    if not record_find:
        auction_type = event['auction_type']

        if auction_type == 'english':
            return 

        current_price = str(float(event['ending_price']) /  math.pow(10,18))
        listing_time = event['listing_time']

        record_find = {
            'token_id': asset['token_id'],
            'traits': [],
            'score': "0",
            'current_price': current_price,
            'listing_time': listing_time,
            'is_notice':"0"
        }

        db[slug].insert_one(record_find)
        
    else:
        record_find_list_time = record_find['listing_time']
        listing_time = event['listing_time']

        if listing_time >= record_find_list_time:
            current_price = str(float(event['ending_price']) /  math.pow(10,18))
            newvalues = { "$set": { 
                    "current_price": current_price, 
                    "listing_time":listing_time,
                    "is_notice":"0"
                } 
            }
            db[slug].update_one({ "token_id": token_id }, newvalues)
    
    if record_find['score'] == "0":
        assets = utility.getAssets(contract_address,0,{"token_ids":[token_id]})
        for asset in assets['assets']:
            token_id = asset['token_id']
            traits = asset['traits']
            if len(traits) <= 1:
                continue
            score = str(utility.getAssetsRarityScore(traits,total_supply))
            newvalues = { "$set": { 
                    "traits": traits,
                    "score": score
                }
            }
            db[slug].update_one({ "token_id": token_id }, newvalues)

    with_score = list(db[slug].find({ "score": { "$gt": 0 } }))
    with_score_len = len(with_score)

    if with_score_len < total_supply/10:
        print("with_score_len = {} supply / 10 = {}".format(with_score_len,total_supply))
        return 

    with_score_sorted = sorted(with_score, key=lambda x: x['score'], reverse=True)
    index = next((i for i, item in enumerate(with_score_sorted) if item['token_id'] == token_id), -1)
    if index < 0:
        return 
    if index < total_supply * 0.15:
        if record_find['is_notice'] == "0" or record_find['is_notice'] > str(index/with_score_len):
            message = "[link](https://opensea.io/assets/{}/{})\n{}/{}".format(contract_address,token_id,index+1,with_score_len)
            utility.notify(message)
            newvalues = { "$set": { 
                    "is_notice": str(index/with_score_len),
                }
            }
            db[slug].update_one({ "token_id": token_id }, newvalues)
        
if __name__ == '__main__':
    slug =utility.listenSlug()
    collection_detail = utility.getCollection(slug)
    print(collection_detail)
    contract_address = collection_detail['collection']['primary_asset_contracts'][0]['address']
    total_supply = int(collection_detail['collection']['stats']['total_supply'])

    db = utility.initDB()
    while True:
        events = utility.getCreatedOrderEvent(contract_address)
        for event in events['asset_events']:
            storeEvent(event,slug,total_supply)
        utility.delay(30)