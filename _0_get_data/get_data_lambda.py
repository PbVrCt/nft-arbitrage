import json
import time
import random

# import os
# import datetime
# import pathlib
# from collections import Counter

import requests

from queries import query, variables

URL = "https://axieinfinity.com/graphql-server-v2/graphql"

jsn = []


def get_data(
    name,
    part=None,
    classs=None,
    pureness=None,
    breedCount=None,
    hp=None,
    skill=None,
    speed=None,
    morale=None,
    sort="Latest",
):
    empty_request_streak = 0
    print(f"\nQuerying by: {part}, {classs},{breedCount},{pureness}")
    for i in range(0000, 200, 100):
        request = requests.post(
            URL,
            json={
                "query": query,
                "variables": variables(
                    fromm=i,
                    parts=part,
                    classes=classs,
                    pureness=pureness,
                    breedCount=breedCount,
                    hp=hp,
                    skill=skill,
                    speed=speed,
                    morale=morale,
                    sort=sort,
                ),
            },
        )
        try:
            assert request.status_code == 200
        except AssertionError:
            print(f"Unexpected status code returned: {request.status_code}")
            time.sleep(10)
            break
        try:
            jsn_data = request.json()["data"]["axies"]["results"]
            try:
                assert len(jsn_data) != 0
            except AssertionError:
                empty_request_streak += 1
                print("Empty request response")
                if empty_request_streak > 4:
                    print("Moving onto the next query")
                    save_data(data=jsn, name=str(part))
                    return
            else:
                empty_request_streak = 0
        except:
            print("Request response in the wrong format")
        else:
            not_parsed_axies = 0
            for ax in jsn_data:
                if ax["battleInfo"]["banned"] == False:
                    try:
                        id_ = ax["id"]
                        class_ = ax["class"]
                        price = ax["auction"]["currentPriceUSD"]
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
                    except:
                        not_parsed_axies += 1
                    else:
                        jsn.append(
                            {
                                "Id": id_,
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
    return


# Mech : Beast + Bug
# Dawn : Aquatic + Bird
# Dusk : Reptile + Plant
for classs in [
    "Aquatic",
    "Beast",
    "Bird",
    "Bug",
    "Plant",
    "Reptile",
    "Mech",
    "Dawn",
    "Dusk",
]:
    get_data(name=str(classs), classs=classs)
return jsn  # give name based on date

# TODO:
# Option 1: Upload to s3 through the aws console
# Option 2: Switch from lambda to an ECS instance
