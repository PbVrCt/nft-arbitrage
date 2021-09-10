# TODO: Add proxies and asynchronous code
# TODO: Populate dataset
# TODO: Feed the data to aws s3 and then aws sagemaker

# TODO: Move the filters and the notifications to aws kinesis and lambda. Fill stream name below. Check the record weights in kinesis
# TODO: Place the code in a cloudfront yaml file
# TODO: Optimize json sizes and code speed
import json
import time
import random
import uuid
import sys
import os
from collections import Counter

import urllib3
import requests
import pandas as pd
import boto3
import discord
from dotenv import load_dotenv


load_dotenv()
SCRAPER_API_KEY = os.environ["KEY"]

query = """
query GetAxieLatest($auctionType: AuctionType, $criteria: AxieSearchCriteria, $from: Int, $sort: SortBy, $size: Int, $owner: String) {
  axies(auctionType: $auctionType, criteria: $criteria, from: $from, sort: $sort, size: $size, owner: $owner) {
    results {
      ...AxieBrief
    }
  }
}

fragment AxieBrief on Axie {
  id
  breedCount
  image
  auction {
    currentPrice
    currentPriceUSD
  }
  battleInfo {
    banned
  }
  parts {
    name
    class
    type
    specialGenes
  }
}
"""


def variables(fromm):
    return {
        "from": fromm,
        "size": 100,
        "sort": "PriceAsc",
        "auctionType": "Sale",
        "owner": None,
        "criteria": {
            "region": None,
            "parts": None,
            "bodyShapes": None,
            "classes": None,
            "stages": None,
            "numMystic": None,
            "pureness": None,
            "title": None,
            "breedable": None,
            "breedCount": None,
            "hp": [],
            "skill": [],
            "speed": [],
            "morale": [],
        },
    }


url = "https://axieinfinity.com/graphql-server-v2/graphql"
# proxies = {
#     "http": f"http://scraperapi:{SCRAPER_API_KEY}@proxy-server.scraperapi.com:8001"  # https to hit the proxy
# }
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# client = boto3.client('kinesis',region_name='eu-west-1')
partition_key = str(uuid.uuid4())
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
webhook = discord.Webhook.from_url(
    DISCORD_WEBHOOK_URL, adapter=discord.RequestsWebhookAdapter()
)

# Filter by build
leaderboard = pd.read_csv("leaderboard.csv")
leaderboard = (
    leaderboard[["Back", "Mouth", "Horn", "Tail"]].drop_duplicates().values.tolist()
)
BEST_BUILDS = set(tuple(x) for x in leaderboard)
# Don´t retrieve the same nft twice
bargains = set()

while True:
    for i in range(80):
        fromm = 500 + (i * 1000)  # (500,80500)
        n_found = 0
        request = requests.post(
            url,
            # proxies=proxies,
            json={"query": query, "variables": variables(fromm=fromm)},
            verify=False,
        )
        if request.status_code == 200:
            jsn_data = request.json()
        else:
            raise Exception(f"Unexpected status code returned: {request.status_code}")
        try:
            jsn_data = request.json()["data"]["axies"]["results"]
            jsn = []
            for ax in jsn_data:
                try:
                    if ax["battleInfo"]["banned"] == False:
                        id_ = ax["id"]
                        price = ax["auction"]["currentPriceUSD"]
                        breedCount = ax["breedCount"]
                        pureness = Counter(
                            [
                                ax["parts"][0]["class"],
                                ax["parts"][1]["class"],
                                ax["parts"][2]["class"],
                                ax["parts"][3]["class"],
                                ax["parts"][4]["class"],
                                ax["parts"][5]["class"],
                            ]
                        ).most_common(1)[0][1]
                        eyes = ax["parts"][0]["name"]
                        ears = ax["parts"][1]["name"]
                        back = ax["parts"][2]["name"]
                        mouth = ax["parts"][3]["name"]
                        horn = ax["parts"][4]["name"]
                        tail = ax["parts"][5]["name"]
                        jsn.append(
                            f"id={id_},price={price},breedCount={breedCount},pureness={pureness},eyes={eyes},ears={ears},back={back},mouth={mouth},horn={horn},tail={tail}"
                        )
                    # Discord notification
                    build = tuple([back, mouth, horn, tail])
                    if (
                        # (30.0 < float(price) < 300.0)
                        (build in BEST_BUILDS)
                        # and (breedCount < 3)
                        # and (pureness > 3)
                        and (id_ not in bargains)
                    ):
                        webhook.send(
                            f"""
                            https://marketplace.axieinfinity.com/axie/{id_}
                            price: {price} usd
                            breedCount: {breedCount} 
                            pureness: {pureness} 
                            """,
                            embed=discord.Embed().set_image(url=ax["image"]),
                        )
                        n_found += 1
                        bargains.add(id_)
                except:
                    print("Error parsing axie")
        except:
            print("Failed request")
        # else:
        #     client.put_record(
        #         StreamName="stream_name", Data=jsn, PartitionKey=partition_key
        #     )
        print(
            f"\nSorted by price: {fromm}-{fromm+100}",
            f"\nAmount of bargains: {n_found}",
            "\n*******",
        )
        time.sleep(random.lognormvariate(0.7, 0.5))
