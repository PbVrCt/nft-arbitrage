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


def get_data(name, part=None, classs=None):
    jsn = []
    empty_request_streak = 0
    print(f"\nQuerying by: {part}, {classs}")
    for i in range(0, 10000, 100):
        request = requests.post(
            URL,
            json={
                "query": query,
                "variables": variables(fromm=i, parts=part, classes=classs),
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
    save_data(data=jsn, name=name)
    return


if __name__ == "__main__":
    # There are 131 parts. Might be better to split the this up
    # 0:15 done
    # 120:125 done
    # 65 : 77 done
    # 53  dawn  done
    for classs in ["Dawn"]:
        for part in parts[54:60]:
            get_data(name=str(part) + str(classs), classs=classs, part=part)
        # get_data(name=part, part=part)
    #     get_data(name=classs, classs=classs)
    # Dusk, Dawn, Mech, Bug   done
