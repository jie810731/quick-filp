import utility
import threading
import random


def updateTraits(db,slug,contract_address,token_ids,total_supply):
    assets = utility.dataOfRetryUntilResponseOk(utility.getAssetsResponse(contract_address,{"token_ids":token_ids}))
    try:
        assets_data = assets['assets']
    except KeyError:
        assets_data = []
    except :
        assets_data = []

    for asset in assets_data:
        token_id = asset['token_id']
        traits = asset['traits']
        if len(traits) <= 1:
            continue
        score = utility.getAssetsRarityScore(traits,total_supply)
        newvalues = { "$set": { 
                "traits": traits,
                "score": score
            }
        }
        db[slug].update_one({ "token_id": token_id }, newvalues)
        
        print("update token_id = {} trait success".format(token_id))

if __name__ == '__main__':
    slug = utility.listenSlug()
    
    traits = {}
    while len(traits) < 2 :
        collection_detail = utility.dataOfRetryUntilResponseOk(utility.getCollectionResponse(slug))  
        traits = collection_detail['collection']['traits']

        if len(traits) > 1:
            break

        print("collection is not reveal delay 10 sec")
        utility.delay(10)

    contract_address = collection_detail['collection']['primary_asset_contracts'][0]['address']
    total_supply = int(collection_detail['collection']['stats']['total_supply']) 
    
    db = utility.initDB()

    is_need_update = True

    while is_need_update:
        need_update_traits = list(db[slug].find({"score":0.0}))

        if len(need_update_traits) == 0 and db[slug].count_documents({}) != 0:
            print('update trait finish')
            is_need_update = False
        #有帶token id的話最多只能30筆 
        n = 30
        groups = [need_update_traits[k:k+n] for k in range(0, len(need_update_traits), n)]

        for index,group in enumerate(groups):
            token_ids = [x["token_id"] for x in group]

            threading.Thread(target = updateTraits,args = (db,slug,contract_address,token_ids,total_supply,)).start()
        
            if (index+1) % 4 == 0:
                print('break')
                utility.delay(6)

