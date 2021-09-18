import json
import time
import random
import os
import datetime
import pathlib
from collections import Counter

import urllib3
import requests

from queries import query, variables, parts

URL = "https://axieinfinity.com/graphql-server-v2/graphql"
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def save_data(data, name):
    start_date = str(datetime.date.today())
    # Create the folder if it doens't exist
    path = pathlib.Path(__file__).resolve().parent / f"../data/{start_date}"
    path.mkdir(parents=True, exist_ok=True)
    # Remove data if it already exists
    if os.path.isfile(f"../data/{start_date}/{name}.json"):
        os.remove(f"../data/{start_date}/{name}.json")
    # Save the data
    with open(f"./data/{start_date}/{name}.json", "w") as f:
        json.dump(data, f)
    return


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
    sort="PriceAsc",
):
    jsn = []
    empty_request_streak = 0
    print(f"\nQuerying by: {part}, {classs}")
    for i in range(0, 10000, 400):
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
            verify=False,
        )
        try:
            assert request.status_code == 200
        except AssertionError:
            print(f"Unexpected status code returned: {request.status_code}")
            time.sleep(10)
            break
        try:
            a = request.json()
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
    save_data(data=jsn, name=name)
    return


if __name__ == "__main__":
    # There are 131 parts. Might be better to split this up
    # 0-21 Aquatic
    # 21-43 Beast
    # 44-65 Bird
    # 66 - 87 Bug
    # 88 - 109 Plant
    # 110 - 131 Reptile
    # Mech : Beast + Bug
    # Dawn : Plant + Bird
    # Dusk : Reptile + Aquatic

    for part in parts[0:131]:
        get_data(name=part, part=part)

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
        get_data(name=str(part) + "PriceDesc", classs=classs, sort="PriceDesc")

    # for classs in ["Mech"]:
    #     for part in parts[25:35]:
    #         get_data(name=str(part) + str(classs), classs=classs, part=part)
    #     for part in parts[70:80]:
    #         get_data(name=str(part) + str(classs), classs=classs, part=part)

    # for classs in ["Dawn"]:
    #     for part in parts[50:60]:
    #         get_data(name=str(part) + str(classs), classs=classs, part=part)
    #     for part in parts[95:105]:
    #         get_data(name=str(part) + str(classs), classs=classs, part=part)

    # for classs in ["Dusk"]:
    #     for part in parts[5:15]:
    #         get_data(name=str(part) + str(classs), classs=classs, part=part)
    #     for part in parts[115:125]:
    #         get_data(name=str(part) + str(classs), classs=classs, part=part)
