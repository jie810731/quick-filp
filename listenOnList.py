from numpy import record
import utility
import math

if __name__ == '__main__':
    slug =utility.listenSlug()
    collection_detail = utility.dataOfRetryUntilResponseOk(utility.getCollectionResponse(slug)) 
    contract_address = collection_detail['collection']['primary_asset_contracts'][0]['address']
    total_supply = int(collection_detail['collection']['stats']['total_supply'])

    db = utility.initDB()
    while True:
        with_score = list(db[slug].find({ "score": { "$gt": 0 } }))
        with_score_sorted = sorted(with_score, key=lambda x: x['score'], reverse=True)
        print('with score len = {}'.format(len(with_score_sorted)))
        if len(with_score) < total_supply * 0.25:
            print('no enough score data')
            utility.delay(10)

            continue
        
        on_list = list(db[slug].find({'listing_time' : { "$exists": True, "$ne": '' }  }))
        print('on the list len = {}'.format(len(on_list)))
        for item in on_list:
            token_id = item['token_id']
            index = next((i for i, item in enumerate(with_score_sorted) if item['token_id'] == token_id), -1)

            if index < 0:
                continue 
            
            if index > int(len(with_score_sorted) * 0.05):
                continue

            if item['is_notice'] == False:
    
                message = "[link](https://opensea.io/assets/{}/{})\n token id = {} rank = {}/{}/{}  {} \n price = {}".format(contract_address,token_id,token_id,index+1,len(with_score_sorted),total_supply,(index+1)/len(with_score_sorted)*100,item['current_price'])
                utility.notify(message)
                newvalues = { "$set": { 
                        "is_notice": True,
                    }
                }
        
                db[slug].update_one({ "token_id": str(token_id) }, newvalues)
            
        utility.delay(30)