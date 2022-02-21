import utility
import pymongo
import math

if __name__ == '__main__':
    slug =utility.listenSlug()

    collection_detail = utility.dataOfRetryUntilResponseOk(utility.getCollectionResponse(slug))
    total_supply = int(collection_detail['collection']['stats']['total_supply']) 
    
    contract_address = collection_detail['collection']['primary_asset_contracts'][0]['address']
    
    client = pymongo.MongoClient("mongodb://mongodb:27017/")
    db = client.myCollection

    offset = 0
    assets = True
    while assets:
        insert_datas = []
        assets = utility.dataOfRetryUntilResponseOk(utility.getAssetsResponse(contract_address,{"offset":offset}))
        try:
            assets = assets['assets']
        except:
            assets =[]

        for asset in assets:
            token_id = asset['token_id']
            record_find = db[slug].find_one({ "token_id": token_id })
            if  record_find:

                continue

            current_price = utility.getListingPrice(asset)
            insert = {
                'token_id': asset['token_id'],
                'traits': [],
                'trait_count':0,
                'score': 0.0,
                'current_price':current_price,
                "is_notice":False,
                "listing_time":""
            }
            if current_price != '0':
                insert['listing_time'] = asset['sell_orders'][0]['created_date']

            insert_datas.append(insert)
        if  insert_datas:
            db[slug].insert_many(insert_datas)

        offset += len(assets)
        print('insert data offset = {}'.format(offset))
        
    print('insert data end')
