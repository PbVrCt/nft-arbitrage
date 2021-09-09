# TODO: Move the filters and the notifications to aws kinesis and lambda. Fill stream name below. Check the record weights in kinesis
# TODO: Explore queries in postman, add more filters
# TODO: Place this code in a cloudfront yaml file
# TODO: Optimize json sizes and code speed
# TODO: Increase amount of shards and add concurrency using proxies and asynchronous code
# TODO: Feed the data to aws s3 and then aws sagemaker
import json
import time
import random
import uuid
import sys
import os
from collections import Counter

import urllib3
import requests
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
    id
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
            "pureness": 6,
            "title": None,
            "breedable": None,
            "breedCount": 0,
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
sucesses = 0
failures = 0
# client = boto3.client('kinesis',region_name='eu-west-1')
partition_key = str(uuid.uuid4())
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]
webhook = discord.Webhook.from_url(
    discord_webhook, adapter=discord.RequestsWebhookAdapter()
)
bargains = set()
while True:
    for i in range(1):  # 100*i
        request = requests.post(
            url,
            # proxies=proxies,
            json={"query": query, "variables": variables(i * 100)},
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
                        eyes = ax["parts"][0]["id"]
                        ears = ax["parts"][1]["id"]
                        back = ax["parts"][2]["id"]
                        mouth = ax["parts"][3]["id"]
                        horn = ax["parts"][4]["id"]
                        tail = ax["parts"][5]["id"]
                        jsn.append(
                            f"id={id_},price={price},breedCount={breedCount},pureness={pureness},eyes={eyes},ears={ears},back={back},mouth={mouth},horn={horn},tail={tail}"
                        )
                    # Discord notification
                    if (
                        30.0
                        < float(price)
                        < 260.0
                        # and (breedCount < 3)
                        # and (pureness > 3)
                    ):
                        if id_ not in bargains:
                            webhook.send(
                                f"""
                                https://marketplace.axieinfinity.com/axie/{id_}
                                price: {price} usd
                                breedCount: {breedCount} 
                                pureness: {pureness} 
                                """,
                                embed=discord.Embed().set_image(url=ax["image"]),
                            )
                        bargains.add(id_)
                except:
                    print("Error parsing axie")
            # jsn = json.dumps(jsn, indent=2)
            # print(jsn)
            sucesses += 1
        except:
            failures += 1
        # else:
        #     client.put_record(
        #         StreamName="stream_name", Data=jsn, PartitionKey=partition_key
        #     )

        # end = time.time()
        # print("Time elapsed: ", end - start, "s")
        # print("Estimated size: " + str(sys.getsizeof(jsn) / 1024) + "KB")
        time.sleep(random.lognormvariate(0.7, 0.5))
    print(
        "Sucessful requests: ", sucesses, "\nFailed requests: ", failures, "\n*******"
    )
