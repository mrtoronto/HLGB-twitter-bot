import os
import requests
import json
from datetime import datetime
from local_settings import *
from twitter.api import Api
import time

twitter_api = Api(consumer_key, consumer_secret, access_token, access_token_secret)

def get_recent_trxn(max_results=10,
                    API_KEY = ETHER_API_KEY):
    url = f"https://api.etherscan.io/api?module=account&action=tokennfttx&page=1&offset={max_results}&sort=desc&contractaddress={contract_address}&apikey={API_KEY}"
    return json.loads(requests.get(url).text)['result']


def get_trxn_value(trxn_id, API_KEY = ETHER_API_KEY):
    url = f"https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={trxn_id}&apikey={API_KEY}"
    trxn_value = int(json.loads(requests.get(url).text)['result']['value'], 16) / 1e18
    return trxn_value

def get_value_from_OS(token_id):
    url = "https://api.opensea.io/api/v1/events"

    querystring = {"asset_contract_address":contract_address,
                   "token_id":token_id,
                   "event_type":"successful",
                   "only_opensea":"false",
                   "offset":"0",
                   "limit":"1"}

    headers = {"Accept": "application/json"}
    response = requests.request("GET", url, headers=headers, params=querystring)

    return int(json.loads(response.text)['asset_events'][0]['total_price']) / 1e18

def add_values(trxns):
    for trxn in trxns:
        value = get_trxn_value(trxn['hash'])
        if not value:
            value = get_value_from_OS(trxn['token_id'])
        trxn.update({'value': value})
    return trxns

def update_timestamp(trxns, dt_format='%Y-%m-%d %H:%M:%S'):
    for trxn in trxns:
        ts = int(trxn['timeStamp'])
        trxn.update({'timeStamp': datetime.utcfromtimestamp(ts).strftime(dt_format)})
    return trxns

def clean_trxns(trxns):
    return [{'timeStamp' : t['timeStamp'], 
             'hash': t['hash'],
             'to': t['to'], 
             'from': t['from'], 
             'token_id': t['tokenID'],
             'value': t['value']} for t in trxns]

def remove_tweeted_trxn(trxns, tweeted_hashes):
    return [t for t in trxns if t['hash'] not in tweeted_hashes]

def send_tweets(trxns):
    for t in trxns:
        tweet_str = f'Bear #{t["token_id"]} was purchased for {t["value"]} ETH'
        tweet_str += f' by https://opensea.io/accounts/{t["to"]} from https://opensea.io/accounts/{t["from"]}\n\n'
        tweet_str += f'https://opensea.io/assets/{contract_address}/{t["token_id"]}'
        try:
            status = twitter_api.PostUpdate(tweet_str)
            print(f'Tweeted {tweet_str}')
            time.sleep(1)
        except:
            pass
        




def main():
    if os.path.exists('tweeted_hashes.txt'):
        with open('tweeted_hashes.txt', 'r') as f:
            tweeted_hashes = set(f.read().split('\n'))
    else:
        tweeted_hashes = set()

    while True:
        start_time = time.time()
        print('Getting transactions')
        trxns = get_recent_trxn()
        trxns = add_values(trxns)
        trxns = update_timestamp(trxns)
        trxns = clean_trxns(trxns)
        trxns = remove_tweeted_trxn(trxns, tweeted_hashes)
        print(f'Tweeting {len(trxns)} tweets..')
        send_tweets(trxns)

        [tweeted_hashes.add(t['hash']) for t in trxns]

        with open('tweeted_hashes.txt', 'w') as f:
            f.write("\n".join(tweeted_hashes))
        print(f"Loop took {time.time() - start_time}s. Sleeping...")
        time.sleep(60)
    

if __name__ == "__main__":
    main()