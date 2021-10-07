import json
import time
import random
import os
import datetime
import pathlib

# import urllib3
import requests

from _0_get_data.queries import query, variables, parts

URL = "https://axieinfinity.com/graphql-server-v2/graphql"
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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
    sort="Latest",
):
    jsn = []
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
            # verify=False,
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
                        price = ax["auction"]["currentPrice"]
                        priceUSD = ax["auction"]["currentPriceUSD"]
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
                                "PriceBy100": float(price) * 1e-16,
                                "PriceUSD": float(priceUSD),
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


# Mech : Beast + Bug
# Dawn : Aquatic + Bird
# Dusk : Reptile + Plant
start = time.time()
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
end = time.time()
print("Time elapsed collecting data: ", end - start, "s\n")


# for breedCount in [0, 1, 2, 3, 4, 5, 6]:
#     for pureness in [2, 3, 4, 5, 6]:
#         for part in parts[0:131]:
#             get_data(
#                 name=str(breedCount) + str(pureness) + str(part),
#                 part=part,
#                 breedCount=breedCount,
#                 pureness=pureness,
#             )

# for classs in ["Mech"]:
#     for part in parts[21:43]:
#         get_data(name=str(part) + str(classs), classs=classs, part=part)
#     for part in parts[66:87]:
#         get_data(name=str(part) + str(classs), classs=classs, part=part)

# for classs in ["Dawn"]:
#     for part in parts[44:65]:
#         get_data(name=str(part) + str(classs), classs=classs, part=part)
#     for part in parts[0:21]:
#         get_data(name=str(part) + str(classs), classs=classs, part=part)

# for classs in ["Dusk"]:
#     for part in parts[88:109]:
#         get_data(name=str(part) + str(classs), classs=classs, part=part)
#     for part in parts[110:131]:
#         get_data(name=str(part) + str(classs), classs=classs, part=part)
