import json
import time
import random
import os
import datetime
import pathlib

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
            "breedCount": 6,
            "hp": [],
            "skill": [],
            "speed": [],
            "morale": [],
        },
    }


# Pureness, BreedCount, Classes, Stats, Parts. Use script
# The api is limiting data retrieval to the first 10 000 nfts for a given query filter. So I'm querying by different filters
DTSET_NAME = "breedcount6"

URL = "https://axieinfinity.com/graphql-server-v2/graphql"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
start_date = str(datetime.date.today())

# For some reason I cannot save 10 000 rows of json at once so i do batches and then append them
jsn = []
for batch in range(0, 2):  # (0,10000)
    start = batch * 5000
    end = batch * 5000 + 5000
    for i in range(start, end, 100):
        request = requests.post(
            URL,
            json={"query": query, "variables": variables(fromm=i)},
            verify=False,
        )
        if not request.status_code == 200:
            raise Exception(f"Unexpected status code returned: {request.status_code}")
        try:
            a = request.json()
            jsn_data = request.json()["data"]["axies"]["results"]
            assert len(jsn_data) != 0
        except:
            print("Request response in wrong format or empty")
        else:
            not_parsed_axies = 0
            for ax in jsn_data:
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
                                "Id": id_,
                                "BreedCount": breedCount,
                                "Pureness": pureness,
                                "Class": class_,
                                "Eyes": eyes,
                                "Ears": ears,
                                "Back": back,
                                "Mouth": mouth,
                                "Horn": horn,
                                "Tail": tail,
                                "Price": price,
                            }
                        )

            print(
                f"Sorted by price: {i}-{i+100}",
                f"\nn_axies failed to parse: ",
                not_parsed_axies,
                "/",
                len(jsn_data),
            )
        time.sleep(random.lognormvariate(0.7, 0.5))

path = pathlib.Path(__file__).resolve().parent / f"data/{start_date}"
path.mkdir(parents=True, exist_ok=True)
# Remove data if it already exists
if os.path.isfile(f"../data/{start_date}/{DTSET_NAME}.json"):
    os.remove(f"../data/{start_date}/{DTSET_NAME}.json")
# Save data
with open(f"../data/{start_date}/{DTSET_NAME}.json", "w") as f:
    json.dump(jsn, f)
