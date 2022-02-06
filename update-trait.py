import utility
import threading
import random


def updateTraits(db,slug,contract_address,token_ids,total_supply):
    assets = utility.getAssets(contract_address,0,{"token_ids":token_ids})
    for asset in assets['assets']:
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

if __name__ == '__main__':
    slug =utility.listenSlug()
    collection_detail = utility.getCollection(slug)
    contract_address = collection_detail['collection']['primary_asset_contracts'][0]['address']
    total_supply = int(collection_detail['collection']['stats']['total_supply'])

    db = utility.initDB()
    # myquery = { "score": { "$gt": 0 } }
    # newvalues = { "$set": { "score": "0" } }

    # x = db[slug].update_many(myquery, newvalues)
    # quit()
    # print('a')
    is_need_update = True
    while is_need_update:
        need_update_traits = list(db[slug].find({"score":"0"}))
        # print(need_update_traits)
        if len(need_update_traits) == 0:
            is_need_update = False
        n = 30
        groups = [need_update_traits[k:k+n] for k in range(0, len(need_update_traits), n)]

        for index,group in enumerate(groups):
            token_ids = [x["token_id"] for x in group]
            # updateTraits(db,slug,contract_address,token_ids,total_supply)
            threading.Thread(target = updateTraits,args = (db,slug,contract_address,token_ids,total_supply,)).start()
            # print(index)
            # print(index+1 % 10)
            if (index+1) % 5 == 0:
                print('break')
                utility.delay(10)

