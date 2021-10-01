class_stats = {
    "Beast": [31, 35, 31, 43],
    "Aquatic": [39, 39, 35, 27],
    "Plant": [43, 31, 31, 35],
    "Bird": [27, 43, 35, 35],
    "Bug": [35, 31, 35, 39],
    "Reptile": [39, 35, 31, 35],
    "Dusk": [43, 39, 27, 31],
    "Mech": [31, 39, 43, 27],
    "Dawn": [35, 35, 39, 31],
}
part_stats = {
    "Beast": [0, 1, 0, 3],
    "Aquatic": [1, 3, 0, 0],
    "Plant": [3, 0, 0, 1],
    "Bird": [0, 3, 0, 1],
    "Bug": [1, 0, 0, 3],
    "Reptile": [3, 1, 0, 0],
}


def engineer_combos(df):
    df = df.copy()
    df.loc[:, "Back-Mouth"] = df["Back"] + "/" + df["Mouth"]
    df.loc[:, "Back-Horn"] = df["Back"] + "/" + df["Horn"]
    df.loc[:, "Back-Tail"] = df["Back"] + "/" + df["Tail"]
    df.loc[:, "Mouth-Horn"] = df["Mouth"] + "/" + df["Horn"]
    df.loc[:, "Mouth-Tail"] = df["Mouth"] + "/" + df["Tail"]
    df.loc[:, "Horn-Tail"] = df["Horn"] + "/" + df["Tail"]
    df.loc[:, "Back-Mouth-Horn"] = df["Back"] + "/" + df["Mouth"] + "/" + df["Horn"]
    df.loc[:, "Back-Mouth-Tail"] = df["Back"] + "/" + df["Mouth"] + "/" + df["Tail"]
    df.loc[:, "Back-Horn-Tail"] = df["Back"] + "/" + df["Horn"] + "/" + df["Tail"]
    df.loc[:, "Mouth-Horn-Tail"] = df["Mouth"] + "/" + df["Horn"] + "/" + df["Tail"]
    df.loc[:, "Build"] = (
        df["Back"] + "/" + df["Mouth"] + "/" + df["Horn"] + "/" + df["Tail"]
    )
    return df


combos = [
    "Back-Mouth",
    "Back-Horn",
    "Back-Tail",
    "Mouth-Horn",
    "Mouth-Tail",
    "Horn-Tail",
]
tricombos = ["Back-Mouth-Horn", "Back-Mouth-Tail", "Back-Horn-Tail", "Mouth-Horn-Tail"]
build = ["Build"]

# From axie zone
card_scores = {
    **dict.fromkeys(
        [
            "Pigeon Post",
            "Tri Spikes",
            "Bidens",
            "Post Fight",
            "Croc",
            "Bone Sail",
            "Fish Snack",
            "Arco",
            "Perch",
            "Incisor",
            "Mint",
            "Cerastes",
            "Wall Gecko",
            "Caterpillars",
            "Snail Shell",
            "Shoal Star",
            "Hermit",
            "Tiny Turtle",
            "Peace Maker",
            "Eggshell",
            "Goda",
            "Catfish",
            "Sponge",
            "Goldfish",
        ],
        1,
    ),
    **dict.fromkeys(
        [
            "Serious",
            "Red Ear",
            "Beech",
            "Zigzag",
            "Mosquito",
            "Thorny Caterpillar",
            "Lam",
            "Hot Butt",
            "Hatsune",
            "Watermelon",
            "Sandal",
            "Buzz Buzz",
            "Granma's Fan",
            "Feather Spear",
            "Jaguar",
            "Navaga",
            "Ranchu",
            "Tadpole",
            "Hare",
            "Balloon",
            "Pocky",
            "Anemone",
            "Pliers",
            "Dual Blade",
            "Shiba",
            "Gila",
            "Doubletalk",
            "Teal Shell",
            "Scarab",
            "Cactus",
            "Swallow",
            "Nut Cracker",
            "Iguana",
            "Scaly Spoon",
            "Scaly Spear",
            "Potato Leaf",
            "Carrot",
            "Herbivore",
            "Bamboo Shoot",
            "Pumpkin",
            "Cute Bunny",
            "Parasite",
            "Garish Worm",
            "Cloud",
            "Hungry Bird",
            "Kestrel",
            "Trump",
            "Raven",
            "Cupid",
            "Merry",
            "Little Branch",
            "Timber",
            "Risky Beast",
            "Piranha",
            "Oranda",
            "Clamshell",
            "Babylonia",
            "Blue Moon",
            "Feather Fan",
            "Nimo",
        ],
        0.5,
    ),
    **dict.fromkeys(
        [
            "Little Owl",
            "Tri Feather",
            "Rice",
            "Confident",
            "Ronin",
            "Razor Bite",
            "Kotaro",
            "Toothless Bite",
            "Rose Bud",
            "Shiitake",
            "Turnip",
            "Leaf Bug",
            "Antenna",
            "Lagging",
            "Wing Horn",
            "Gerbil",
            "Shrimp",
            "Koi",
            "Risky Fish",
            "Axie Kiss",
            "Imp",
        ],
        0.0,
    ),
    **dict.fromkeys(
        [
            "Indian Star",
            "Kingfisher",
            "Furball",
            "Bumpy",
            "Watering Can",
            "Grass Snake",
            "Cuckoo",
            "Cottontail",
            "Tiny Dino",
            "Unko",
            "Ant",
            "Spiky Wing",
            "Silence Whisper",
        ],
        -0.5,
    ),
    **dict.fromkeys(
        [
            "The Last One",
            "Cattail",
            "Pupae",
            "Hero",
            "Green Thorns",
            "Square Teeth",
            "Snake Jar",
            "Yam",
            "Gravel Ant",
            "Twin Tail",
        ],
        -1,
    ),
    **dict.fromkeys(["Pincer", "Strawberry Shortcake"], -2.5),
}

# Attack, Shield, EnergyCost, Stunt, Poison, DmgCombo, Targetting,
# EnergyGain, Buffs/debuffs, CardDraw/Discard, Healing/Shielding/Blocking
card_attributes = {
    "Hermit": [0, 115, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Blue Moon": [120, 30, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    "Goldfish": [110, 20, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Sponge": [60, 90, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Anemone": [80, 40, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Perch": [100, 20, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    "Babylonia": [100, 50, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Teal Shell": [50, 80, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Clamshell": [110, 40, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Oranda": [120, 30, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Shoal Star": [115, 10, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Lam": [110, 40, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Catfish": [80, 30, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Risky Fish": [110, 30, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Piranha": [120, 30, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    "Koi": [110, 30, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Nimo": [30, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    "Tadpole": [110, 40, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Ranchu": [120, 30, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Navaga": [100, 40, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Shrimp": [30, 30, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    "Ronin": [75, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Hero": [60, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    "Jaguar": [115, 35, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    "Risky Beast": [125, 25, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Timber": [50, 100, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Furball": [120, 30, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Little Branch": [125, 25, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Imp": [70, 20, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    "Merry": [65, 85, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Pocky": [125, 20, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Dual Blade": [130, 20, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Arco": [100, 50, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Nut Cracker": [105, 30, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Goda": [80, 40, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    "Axie Kiss": [100, 30, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Confident": [0, 30, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    "Cottontail": [0, 0, 0, 0, 0, 0, 0, 1.5, 0, 0, 0],
    "Rice": [80, 10, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    "Shiba": [120, 30, 1, 0, 0, 1, 0, 0, 1, 0, 0],
    "Hare": [120, 30, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    "Gerbil": [40, 20, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    "Balloon": [40, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    "Cupid": [120, 20, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Raven": [110, 30, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Pigeon Post": [120, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Kingfisher": [130, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    "Tri Feather": [35, 10, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    "Eggshell": [120, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Cuckoo": [0, 40, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    "Trump": [120, 30, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Kestrel": [130, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Wing Horn": [50, 10, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    "Feather Spear": [110, 50, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Doubletalk": [80, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    "Peace Maker": [120, 30, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Hungry Bird": [110, 40, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    "Little Owl": [25, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    "Swallow": [110, 20, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Feather Fan": [40, 90, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "The Last One": [150, 0, 1, 0, 0, 0, 0, 0, -1, 0, 0],
    "Cloud": [100, 50, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    "Granma's Fan": [120, 30, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Post Fight": [120, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1],
    "Snail Shell": [40, 60, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    "Garish Worm": [100, 50, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    "Buzz Buzz": [100, 40, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Sandal": [110, 50, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Scarab": [110, 40, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    "Spiky Wing": [10, 30, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    "Lagging": [40, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    "Antenna": [80, 60, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    "Caterpillars": [100, 50, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Pliers": [110, 30, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Parasite": [80, 50, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    "Leaf Bug": [20, 20, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    "Mosquito": [70, 40, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Pincer": [20, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    "Cute Bunny": [120, 30, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Square Teeth": [60, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "Ant": [30, 80, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Twin Tail": [60, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    "Fish Snack": [60, 80, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    "Gravel Ant": [30, 40, 1, 0.5, 0, 0, 0, 0, 0, 0, 0],
    "Pupae": [60, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    "Thorny Caterpillar": [105, 30, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Turnip": [60, 80, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    "Shiitake": [0, 40, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    "Bidens": [0, 50, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    "Watering Can": [45, 80, 1, 0, 0, 0, 0, 0.5, 0, 0, 0],
    "Mint": [0, 50, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    "Pumpkin": [0, 110, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    "Bamboo Shoot": [80, 70, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Beech": [105, 40, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Rose Bud": [0, 40, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Strawberry Shortcake": [0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 1.5],
    "Cactus": [110, 20, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Watermelon": [30, 50, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    "Serious": [30, 30, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    "Zigzag": [60, 60, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Herbivore": [75, 75, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Silence Whisper": [0, 40, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Carrot": [70, 40, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    "Cattail": [20, 30, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    "Hatsune": [60, 80, 1, 0.5, 0, 0, 0, 0, 0, 0, 0],
    "Yam": [30, 20, 1, 0, 1, 0, 0, 0, 0, 0, 0],
    "Potato Leaf": [70, 80, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Hot Butt": [90, 50, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Bone Sail": [80, 80, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    "Tri Spikes": [80, 50, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    "Green Thorns": [20, 60, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "Indian Star": [20, 80, 1, 0, 0, 1, 0, 0, 0, 0, 1],
    "Red Ear": [10, 135, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Croc": [90, 60, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Unko": [30, 80, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Scaly Spear": [100, 50, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Cerastes": [90, 60, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Scaly Spoon": [80, 40, 1, 0, 0, 1, 0, 0, 0, 0, 1],
    "Incisor": [100, 40, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Bumpy": [90, 30, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Toothless Bite": [20, 40, 1, 0, 0, 0, 1, 0, 0, 0, 0],
    "Kotaro": [80, 20, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    "Razor Bite": [90, 50, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Tiny Turtle": [80, 50, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    "Wall Gecko": [90, 10, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Iguana": [90, 60, 1, 0, 0, 0, 0, 1, 0, 0, 0],
    "Tiny Dino": [80, 40, 1, 0, 0, 1, 0, 0, 0, 0, 0],
    "Snake Jar": [80, 20, 1, 0, 0, 0, 0, 0, 0, 0, 1],
    "Gila": [100, 55, 1, 0, 0, 0, 0, 0, 1, 0, 0],
    "Grass Snake": [10, 20, 0, 0, 1, 0, 0, 0, 0, 0, 0],
}
