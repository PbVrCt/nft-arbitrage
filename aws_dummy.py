# TODO: Implement twilio to a test group chat
# TODO: Move the filters and the notifications to aws kinesis and lambda. Fill stream name below. Check the record weights in kinesis
# TODO: Explore queries in postman, add more filters
# TODO: Place this code in a cloudfront yaml file
# TODO: Optimize json sizes and code speed
# TODO: Increase amount of shards and add concurrency using proxies and asynchronous code
# TODO: Write automated buy/sell smart contracts
import json
import time
import random
import uuid
import sys
import os

import urllib3
import requests
import boto3
from dotenv import load_dotenv

load_dotenv()
SCRAPER_API_KEY = os.environ["KEY"]

query = """
query GetAxieBriefList($auctionType: AuctionType, $criteria: AxieSearchCriteria, $from: Int, $sort: SortBy, $size: Int, $owner: String) {
  axies(auctionType: $auctionType, criteria: $criteria, from: $from, sort: $sort, size: $size, owner: $owner) {
    results {
      ...AxieBrief
    }
  }
}

fragment AxieBrief on Axie {
  id
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
# client = boto3.client('kinesis',region_name='eu-west-1')
partition_key = str(uuid.uuid4())
sucesses = 0
failures = 0
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
while True:
    for i in range(1):  # 100*

        # start = time.time()
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
                # print(ax)
                if ax["battleInfo"]["banned"] == False:
                    id_ = ax["id"]
                    price = ax["auction"]["currentPriceUSD"]
                    # eyes = ax["parts"][0]["class"]
                    jsn.append(f"id={id_},price={price}")
                if 0.0 < float(price) < 200.0:
                    print(id_, price)

            jsn = json.dumps(jsn, indent=2)
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
        # print("Status code: ", request.status_code)
        time.sleep(random.lognormvariate(1, 0.5))
    print(
        "Sucessful requests: ", sucesses, "\nFailed requests: ", failures, "\n*******"
    )
