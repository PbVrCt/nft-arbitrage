import json
import pickle
import time
import uuid
import os
import asyncio
from collections import Counter

import aiohttp
import urllib3
import pandas as pd
import boto3
import discord
from dotenv import load_dotenv

from _1_preprocessing._3_feature_engineering import score_df

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
        "sort": "Latest",
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
            "breedCount": 0,
            "hp": [],
            "skill": [],
            "speed": [],
            "morale": [],
        },
    }


URL = "https://axieinfinity.com/graphql-server-v2/graphql"
PRXY = os.environ["URL"]
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# client = boto3.client('kinesis',region_name='eu-west-1')
# partition_key = str(uuid.uuid4())
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
WEBHOOK = discord.Webhook.from_url(
    DISCORD_WEBHOOK_URL, adapter=discord.RequestsWebhookAdapter()
)


def get_posts(session, start, end, step=100):
    posts = []
    for i in range(int(start), int(end), int(step)):
        posts.append(
            asyncio.create_task(
                session.post(
                    URL,
                    json={"query": query, "variables": variables(fromm=i)},
                    # proxy=PRXY,
                    ssl=False,
                )
            )
        )
    return posts


async def run_posts(start, end, step=100, timeout=10):
    results = []
    timeouts = 0
    bad_format = 0
    timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(timeout=timeout, trust_env=True) as session:
        posts = get_posts(session, start, end, step)
        responses = await asyncio.gather(*posts, return_exceptions=True)
        for response in responses:
            if isinstance(response, asyncio.TimeoutError):
                timeouts += 1
            else:
                if response.status == 200:
                    try:
                        data = await response.json()
                        results.append(data["data"]["axies"]["results"])
                    except:
                        bad_format += 1
                    else:  # (try+assert are not working for me inside async)
                        if len(data["data"]["axies"]["results"]) == 0:
                            bad_format += 1

                else:
                    print(f"Unexpected status code returned: {response.status}")
    print(
        "Request responses in wrong format or empty: ", bad_format, "/", len(responses)
    )
    print("Timed out requests: ", timeouts, "/", len(responses))
    return results


def compare_two_prices(row, id_):
    global n_found
    global bargains
    if (
        (row["Price"] + 400 < row["Prediction"])
        and (row["Price"] > 50)
        and (id_ not in bargains)
    ):
        bargains.add(id_)
        n_found += 1
        WEBHOOK.send(
            f"""
                https://marketplace.axieinfinity.com/axie/{id_}
                price: {row['Price']} usd
                price prediction: {row['Prediction']}
                multiplier_score: {row['multiplier_score']}
                card_score: {row['sum_card_score']}
                combo_score: {row['sum_combo_score']}
                build_score: {row['build_score']}
                breedCount: {row['BreedCount']}
                """,
            embed=discord.Embed().set_image(url=row["Image"]),
        )


def compare_prices(price_comparaison):
    price_comparaison.apply(lambda df: compare_two_prices(df, df.name), axis=1)


# Model
with open("./_2_model_training/_XGBOOST.pkl", "rb") as f:  # XGBOOST,lightGBM,KNN,tree
    model = pickle.load(f)
# One hot encoder for the axie class
with open("./_1_preprocessing/one_hot_encoder.pickle", "rb") as f:
    oh_enc = pickle.load(f)
# Card and combo scores
with open("./_1_preprocessing/scores_lookup.txt") as f:
    for i in f.readlines():
        scores_lookup = i
scores_lookup = eval(scores_lookup)

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
TIMEOUT = 25
STEP = 100  # 500
FIRST_AXIE = 4000
bargains = set()  # Don´t retrieve the same nft twice
#
try:
    while True:
        for i in range(40):
            init = FIRST_AXIE + i * STEP
            f = FIRST_AXIE + STEP + i * STEP
            n_found = 0
            jsn_data = asyncio.run(run_posts(init, f, 100, timeout=TIMEOUT))
            if jsn_data:
                jsn_data = [axie for sublist in jsn_data for axie in sublist]
                not_parsed_axies = 0
                info_batch = pd.DataFrame()
                price_batch = pd.DataFrame()
                image_batch = pd.DataFrame()
                for ax in jsn_data:
                    if ax["battleInfo"]["banned"] == False:
                        try:
                            id_ = ax["id"]
                            class_ = ax["class"]
                            image = ax["image"]
                            price = float(ax["auction"]["currentPriceUSD"])
                            breedCount = ax["breedCount"]
                            eyes = ax["parts"][0]["name"]
                            ears = ax["parts"][1]["name"]
                            back = ax["parts"][2]["name"]
                            mouth = ax["parts"][3]["name"]
                            horn = ax["parts"][4]["name"]
                            tail = ax["parts"][5]["name"]
                            eyes_type = ax["parts"][0]["class"]
                            ears_type = ax["parts"][1]["class"]
                            back_type = ax["parts"][2]["class"]
                            mouth_type = ax["parts"][3]["class"]
                            horn_type = ax["parts"][4]["class"]
                            tail_type = ax["parts"][5]["class"]
                            axie_info = pd.DataFrame(
                                {
                                    "BreedCount": breedCount,
                                    "Class": class_,
                                    "Eyes": eyes,
                                    "Ears": ears,
                                    "Back": back,
                                    "Mouth": mouth,
                                    "Horn": horn,
                                    "Tail": tail,
                                    "EyesType": eyes_type,
                                    "EarsType": ears_type,
                                    "BackType": back_type,
                                    "MouthType": mouth_type,
                                    "HornType": horn_type,
                                    "TailType": tail_type,
                                },
                                index=[id_],
                            )
                            info_batch = info_batch.append(axie_info)
                            price_batch = price_batch.append(
                                pd.DataFrame({"Price": price}, index=[id_])
                            )
                            image_batch = image_batch.append(
                                pd.DataFrame({"Image": image}, index=[id_])
                            )
                        except:
                            not_parsed_axies += 1
                axie_values = score_df(info_batch, scores_lookup, class_encoder=oh_enc)
                price_predictions = axie_values.apply(
                    lambda row: model.predict(row.values.reshape(1, -1))[0], axis=1
                )
                price_comparaisons = pd.concat(
                    [axie_values, price_batch, price_predictions, image_batch], axis=1
                ).rename({0: "Prediction"}, axis=1)
                compare_prices(price_comparaisons)
                print(
                    f"Axies failed to  parse: ",
                    not_parsed_axies,
                    "/",
                    len(jsn_data),
                    f"\nSorted by price: {init}-{f}",
                    f"\nAmount of bargains: {n_found}",
                    "\n*******",
                )
except KeyboardInterrupt:
    print("Exit")
