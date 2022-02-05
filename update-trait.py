import utility
import threading

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
    is_need_update = True
    while is_need_update:
        need_update_traits = list(db[slug].find({"score":"0"}))
        print(need_update_traits)
        if len(need_update_traits) == 0:
            is_need_update = False
        n = 50
        out = [need_update_traits[k:k+n] for k in range(0, len(need_update_traits), n)]
        for test in out:
            token_ids = [[x["token_id"] for x in test]]
            threading.Thread(target = updateTraits,args = (db,slug,contract_address,token_ids,total_supply,)).start()

