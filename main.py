import os
import requests
import json
from datetime import datetime
from local_settings import *
from twitter.api import Api
import time

twitter_api = Api(consumer_key, consumer_secret, access_token, access_token_secret)

def get_recent_trxn(max_results=10,
                    address = "0xf32e1bdE889eCf672FFAe863721C8f7d280F853b", 
                    API_KEY = ETHER_API_KEY):
    url = f"https://api.etherscan.io/api?module=account&action=tokennfttx&page=1&offset={max_results}&sort=desc&contractaddress={address}&apikey={API_KEY}"
    return json.loads(requests.get(url).text)['result']


def get_trxn_value(trxn_id, API_KEY = ETHER_API_KEY):
    url = f"https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={trxn_id}&apikey={API_KEY}"
    trxn_value = int(json.loads(requests.get(url).text)['result']['value'], 16) / 1e18
    return trxn_value

def add_values(trxns):
    for trxn in trxns:
        trxn.update({'value': get_trxn_value(trxn['hash'])})
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
        tweet_str += f' by https://opensea.io/accounts/{t["from"]} from https://opensea.io/accounts/{t["to"]}\n\n'
        tweet_str += f'https://opensea.io/assets/0xf32e1bde889ecf672ffae863721c8f7d280f853b/{t["token_id"]}'
        try:
            status = twitter_api.PostUpdate(tweet_str)
            print(f'Tweeted {tweet_str}')
        except:
            pass
        




def main():
    if os.path.exists('tweeted_hashes.txt'):
        with open('tweeted_hashes.txt', 'r') as f:
            tweeted_hashes = f.read().split('\n')
    else:
        tweeted_hashes = set()

    while True:
        print('Getting transactions')
        trxns = get_recent_trxn()
        trxns = add_values(trxns)
        trxns = update_timestamp(trxns)
        trxns = clean_trxns(trxns)
        trxns = remove_tweeted_trxn(trxns, tweeted_hashes)
        print(f'Tweeting {len(trxns)} tweets..')
        send_tweets(trxns)

        [tweeted_hashes.add(t['hash']) for t in trxns]

        time.sleep(60)
    

if __name__ == "__main__":
    main()