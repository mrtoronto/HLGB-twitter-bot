# HLGB-twitter-bot

This is a twitter bot that scrapes etherscan and tweets new purchases of HappyLand Gummy Bear NFTs.

Right now, main.py is running on a Digital Ocean Droplet and tweeting new purchases to the account [@HLGB_Sales](https://twitter.com/HLGB_Sales).

## Setup

Requires a `local_settings.py` file which will include Etherscan API key, contract address and Twitter API keys.

```
git clone https://github.com/mrtoronto/HLGB-twitter-bot
python3 -m venv venv && source venv/bin/activate && pip3 install -r requirements.txt
python3 main.py
```

