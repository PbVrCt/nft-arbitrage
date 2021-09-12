import json
import time
import random
import os
from collections import Counter

import urllib3
import requests
from dotenv import load_dotenv

load_dotenv()

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
  class
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


URL = "https://axieinfinity.com/graphql-server-v2/graphql"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
jsn = []
for i in range(100, 300101, 100):
    request = requests.post(
        URL,
        json={"query": query, "variables": variables(fromm=i)},
        verify=False,
    )
    if request.status_code == 200:
        jsn_data = request.json()
    else:
        raise Exception(f"Unexpected status code returned: {request.status_code}")
    try:
        jsn_data = request.json()["data"]["axies"]["results"]
    except:
        print("Failed to append request")
    else:
        for ax in jsn_data:
            not_parsed_axies = 0
            if ax["battleInfo"]["banned"] == False:
                try:
                    id_ = ax["id"]
                    class_ = ax["class"]
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
                except:
                    not_parsed_axies += 1
                else:
                    jsn.append(
                        {
                            "id": id_,
                            "breedCount": breedCount,
                            "pureness": pureness,
                            "class": class_,
                            "eyes": eyes,
                            "ears": ears,
                            "back": back,
                            "mouth": mouth,
                            "horn": horn,
                            "tail": tail,
                            "price": price,
                        }
                    )

        print(
            f"Sorted by price: {i}-{i+100}",
            f"\nAxies failed to  parse: ",
            not_parsed_axies,
            "/",
            len(jsn_data),
        )
    time.sleep(random.lognormvariate(0.7, 0.5))
with open("axie_dataset_300_000.json", "w") as f:
    json.dump(jsn, f)
