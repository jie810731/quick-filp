from ast import While
from numpy import record
import utility
import math

if __name__ == '__main__':
    slug =utility.listenSlug()
    collection_detail = utility.getCollection(slug)
    contract_address = collection_detail['collection']['primary_asset_contracts'][0]['address']
    total_supply = int(collection_detail['collection']['stats']['total_supply'])

    db = utility.initDB()
    while True:
        with_score = list(db[slug].find({ "score": { "$gt": 0 } }))
        with_score_sorted = sorted(with_score, key=lambda x: x['score'], reverse=True)
        
        on_list = list(db[slug].find({'listing_time' : { "$exists": True, "$ne": '' }  }))
        for item in on_list:
            token_id = item['token_id']
            index = next((i for i, item in enumerate(with_score_sorted) if item['token_id'] == token_id), -1)

            if index < 0:
                continue 
            if index < total_supply * 0.15:
                if item['is_notice'] == "0" or item['is_notice'] > str(index/len(with_score_sorted)):
                    message = "[link](https://opensea.io/assets/{}/{})\n{}/{}".format(contract_address,token_id,index+1,len(with_score_sorted))
                    utility.notify(message)
                    newvalues = { "$set": { 
                            "is_notice": str(index/len(with_score_sorted)),
                        }
                    }
                    db[slug].update_one({ "token_id": token_id }, newvalues)
            
        utility.delay(30)