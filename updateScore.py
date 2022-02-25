import utility


if __name__ == '__main__':
    db = utility.initDB()
    slug = utility.listenSlug()

    # db[slug].update_many({}, {"$unset": {"average_jaccard_distance":""}})
    # quit()
    
    while db[slug].count_documents({"average_jaccard_distance": { "$exists": False } })  != 0 and db[slug].count_documents({}) == 0:
       utility.delay(10)
    
    max = db[slug].find_one(sort=[("average_jaccard_distance", -1)])['average_jaccard_distance']
    min = db[slug].find_one(sort=[("average_jaccard_distance", 1)])['average_jaccard_distance']
    
    all = list(db[slug].find())

    for item in all:
        score = (item['average_jaccard_distance'] - min) / (max - min) * 100
        newvalues = { "$set": { 
                "score": score
            }
        }

        db[slug].update_one({ "token_id": item['token_id'] }, newvalues)
        print("token id = {} score = {} updated".format(item['token_id'],score))