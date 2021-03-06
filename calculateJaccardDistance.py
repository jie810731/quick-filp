import utility

def updateJaccardDistance(current,all,db):
    sum_jaccard_distance = 0
    for indx,calculate  in enumerate(all):
        if current['token_id'] == calculate['token_id']:
            continue
        jaccard_distance = utility.getJaccardDistance(current['traits'],calculate['traits'])

        sum_jaccard_distance += jaccard_distance
    average_jd = sum_jaccard_distance / (len(all) - 1)

    newvalues = { "$set": { 
            "average_jaccard_distance": average_jd
        }
    }

    db[slug].update_one({ "token_id": current['token_id'] }, newvalues,)  
    print("update jaccard_distance finish token id = {}".format(current['token_id']))

if __name__ == '__main__':
    db = utility.initDB()
    slug = utility.listenSlug()

    # db[slug].update_many({}, {"$unset": {"average_jaccard_distance":""}})
    # quit()

    collection_detail = utility.dataOfRetryUntilResponseOk(utility.getCollectionResponse(slug))
    total_supply = int(collection_detail['collection']['stats']['total_supply'])

    while True:
        all = list(db[slug].find({
            "traits":{
                "$ne":[]
            }
        }))
    
        if len(all) == total_supply:
            break

        utility.delay(10)

    while db[slug].count_documents({"average_jaccard_distance": { "$exists": False } })  != 0:
        item = db[slug].aggregate([
            { "$match": { "average_jaccard_distance": { "$exists": False } } },
            { "$sample": { "size": 1 } }
        ])
        item =next(item,None) 
        
        if not item:
            continue
        
        updateJaccardDistance(item,all,db)

    # item  = db[slug].find_one({"token_id":"4758"})
    # updateJaccardDistance(item,all,db)
