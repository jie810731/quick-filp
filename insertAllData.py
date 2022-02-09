import utility
import pymongo
import math

if __name__ == '__main__':
    slug =utility.listenSlug()
    collection_detail = utility.getCollection(slug)
    collection_traits = None
    try:
        contract_address = collection_detail['collection']['primary_asset_contracts'][0]['address']
        collection_traits = collection_detail['collection']['traits']
    except:
        pass
    
    all_assets = utility.getCollectionAssets(contract_address)

    client = pymongo.MongoClient("mongodb://mongodb:27017/")
    db = client.myCollection

    for asset in all_assets:
        score = utility.getAssetsRarityScore(asset['traits'],len(all_assets))
        current_price = utility.getListingPrice(asset)
        token_id = asset['token_id']
        record_find = db[slug].find_one({ "token_id": token_id })
        if not record_find:
            insert_data = {
                'token_id': asset['token_id'],
                'traits': asset['traits'],
                'score':score,
                'current_price':current_price,
                "is_notice":False,
                "listing_time":""
            }
            if current_price != '0':
                insert_data['listing_time'] = asset['sell_orders'][0]['created_date']

            db[slug].insert_one(insert_data)
        
    print('end')
