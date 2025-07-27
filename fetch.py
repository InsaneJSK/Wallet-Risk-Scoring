import os
import requests
import json
from dotenv import load_dotenv
from tqdm import tqdm
from time import sleep
import pandas as pd

load_dotenv()
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

# Compound V2 function selectors
COMPOUND_SELECTORS = {
    "0xa0712d68": "borrow",
    "0x3b1d21a2": "repayBorrow",
    "0x4e4d9fea": "repayBorrowBehalf",
    "0x1249c58b": "mint",
    "0xe9c714f2": "liquidateBorrow",
}

ETH_PRICE = 3500
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def cached_fetch(url, cache_file, session):
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            return json.load(f)
    try:
        response = session.get(url)
        response.raise_for_status()
        data = response.json()
        with open(cache_file, 'w') as f:
            json.dump(data, f)
        sleep(0.2)  # avoid rate-limiting
        return data
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {"result": []}

def fetch_transactions(wallet_address, session):
    cache_file = f"{CACHE_DIR}/{wallet_address}_txs.json"
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={wallet_address}&startblock=0&endblock=99999999&sort=asc&apikey={ETHERSCAN_API_KEY}"
    return cached_fetch(url, cache_file, session).get("result", [])

def fetch_internal_transactions(wallet_address, session):
    cache_file = f"{CACHE_DIR}/{wallet_address}_internal.json"
    url = f"https://api.etherscan.io/api?module=account&action=txlistinternal&address={wallet_address}&startblock=0&endblock=99999999&sort=asc&apikey={ETHERSCAN_API_KEY}"
    return cached_fetch(url, cache_file, session).get("result", [])

def analyze_wallet(wallet_address, session, cumulative_raw_data):
    txs = fetch_transactions(wallet_address, session)
    internal_txs = fetch_internal_transactions(wallet_address, session)

    # Save raw data for this wallet
    cumulative_raw_data[wallet_address] = {
        "normal": txs,
        "internal": internal_txs
    }

def main():
    session = requests.Session()
    cumulative_raw_data = {}

    df_ids = pd.read_csv("Wallet_id.csv")
    wallet_addresses = df_ids['wallet_id']

    for wallet in tqdm(wallet_addresses, desc="Processing wallets"):
        analyze_wallet(wallet, session, cumulative_raw_data)

    # Save the cumulative raw data
    with open("raw_transaction_data.json", "w") as f:
        json.dump(cumulative_raw_data, f, indent=2)
    print("✅ Saved raw data to raw_transaction_data.json")

if __name__ == "__main__":
    main()
