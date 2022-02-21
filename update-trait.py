import utility
import threading
import random
from web3 import Web3
import requests


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
def getContract(address):
    w3 = Web3(Web3.HTTPProvider("https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"))
    abi = utility.dataOfRetryUntilResponseOk(utility.getAbi(address))['result']
    address  = Web3.toChecksumAddress(address)
    contract  = w3.eth.contract(address=address , abi=abi)

    return contract

def isReveal(contract):
    tokenURI = contract.functions.tokenURI(1).call()
    if tokenURI.startswith('ipfs://'):
        replace = tokenURI.replace("://", "/")
        tokenURI = "https://opensea.mypinata.cloud/{}".format(replace)
    try:
        res = requests.get(url=tokenURI)
    except Exception as ex:
        print(ex)
        pass
    result = res.json()
    
    try:
        attributes = result['attributes']
        unreveal = next((x for x in attributes if x['value'] == 'Unrevealed'), None)
        if len(attributes) <2:
            return False

        if unreveal:
            return False
    except:
        return False

    return True

def updateTraitByWeb3(contract,token_id,db):
    tokenURI = contract.functions.tokenURI(int(token_id)).call()
    if tokenURI.startswith('ipfs://'):
        replace = tokenURI.replace("://", "/")
        tokenURI = "https://opensea.mypinata.cloud/{}".format(replace)
    try:
        res = requests.get(url=tokenURI)
    except Exception as ex:
        print(ex)
        pass
    result = res.json()
    attributes = result['attributes']

    newvalues = { "$set": { 
                "traits": attributes,
                "trait_count": len(attributes)
            }
        }
    db[slug].update_one({ "token_id": token_id }, newvalues)

def updateJaccardDistance(current,copy,db):
    sum_jaccard_distance = 0
    for calculate  in copy:
        if current['token_id'] == calculate['token_id']:
            continue
        jaccard_distance = utility.getJaccardDistance(current['traits'],calculate['traits'])

        sum_jaccard_distance += jaccard_distance
    
    average_jd = sum_jaccard_distance / len(copy)

    newvalues = { "$set": { 
            "average_jaccard_distance": average_jd
        }
    }

    db[slug].update_one({ "token_id": item['token_id'] }, newvalues)  
    print("update jaccard_distance finish token id = {}".format(item['token_id']))

# TODO wait for insert trait to db
# updateJaccardDistance time to long 

if __name__ == '__main__':
    slug = utility.listenSlug()
    collection_detail = utility.dataOfRetryUntilResponseOk(utility.getCollectionResponse(slug))
    contract_address = collection_detail['collection']['primary_asset_contracts'][0]['address']
    contract = getContract(contract_address)
    db = utility.initDB()
    isReveal = isReveal(contract)

    if isReveal:
        need_update_traits = list(db[slug].find({"score":0.0}))

        for need_update_trait in need_update_traits:
            threading.Thread(target = updateTraitByWeb3,args = (contract,need_update_trait['token_id'],db,)).start()
            # updateTraitByWeb3(contract,need_update_trait['token_id'])
    
    all = list(db[slug].find())
    for item in all:
        copy = all[:]
        updateJaccardDistance(item,copy,db)
        
        threading.Thread(target = updateJaccardDistance,args = (item,copy,db,)).start()
        
        sum_jaccard_distance = 0
        for calculate  in db[slug].find():
            if item['token_id'] == calculate['token_id']:
                continue
            jaccard_distance = utility.getJaccardDistance(item['traits'],calculate['traits'])

            sum_jaccard_distance += jaccard_distance
        
        average_jd = sum_jaccard_distance / db[slug].count_documents({}) 

        newvalues = { "$set": { 
                "average_jaccard_distance": average_jd
            }
        }

        db[slug].update_one({ "token_id": item['token_id'] }, newvalues)  
        print("update jaccard_distance finish token id = {}".format(item['token_id']))

    max = db[slug].find_one(sort=[("average_jaccard_distance", -1)])['average_jaccard_distance']
    min = db[slug].find_one(sort=[("average_jaccard_distance", 1)])['average_jaccard_distance']
    print(max)
    print(min)

    for item in all:
        score = (item['average_jaccard_distance'] - min) / (max - min) * 100
        newvalues = { "$set": { 
                "score": score
            }
        }

        db[slug].update_one({ "token_id": item['token_id'] }, newvalues)
        print("token id = {} score = {} updated".format(item['token_id'],score))