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


def variables(
    fromm,
    sort="PriceAsc"
    parts=None,
    classes=None,
    pureness=None,
    breedCount=None,
    hp=None,
    skill=None,
    speed=None,
    morale=None,
    size=100,
):
    return {
        "from": fromm,
        "size": size,
        "sort": sort,
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


parts = [
    "Hermit",
    "Blue Moon",
    "Goldfish",
    "Sponge",
    "Anemone",
    "Perch",
    "Babylonia",
    "Tea Shell",
    "Clamshell",
    "Oranda",
    "Shoal Star",
    "Lam",
    "Catfish",
    "Risky Fish",
    "Piranha",
    "Koi",
    "Nimo",
    "Tadpole",
    "Ranchu",
    "Navaga",
    "Shrimp",
    "Ronin",
    "Hero",
    "Jaguar",
    "Risky Beast",
    "Timber",
    "Furball",
    "Little Branch",
    "Imp",
    "Merry",
    "Pocky",
    "Dual Blade",
    "Arco",
    "Nut Cracker",
    "Goda",
    "Axie Kiss",
    "Confident",
    "Cottontail",
    "Rice",
    "Shiba",
    "Hare",
    "Nut Cracker",
    "Gerbil",
    "Ballon",
    "Cupid",
    "Raven",
    "Pigeon Post",
    "Kingfisher",
    "Tri Feather",
    "Eggshell",
    "Cuckoo",
    "Trump",
    "Kestrel",
    "Wing Horn",
    "Feather Spear",
    "Doubletalk",
    "Peace Maker",
    "Hungry Bird",
    "Little Owl",
    "Swallow",
    "Feather Fan",
    "The Last One",
    "Cloud",
    "Granma's Fan",
    "Post Fight",
    "Snail Shell",
    "Garish Worm",
    "Buzz Buzz",
    "Sandal",
    "Scarab",
    "Spiky Wing",
    "Laggin",
    "Antenna",
    "Caterpillars",
    "Pliers",
    "Parasite",
    "Leaf Bug",
    "Mosquito",
    "Pincer",
    "Cute Bunny",
    "Square Teeth",
    "Ant",
    "Twin Tail",
    "Fish Snack",
    "Gravel Ant",
    "Pupae",
    "Thorny Caterpilar",
    "Turnip",
    "Shitake",
    "Bidens",
    "Watering Can",
    "Mint",
    "Pumpkin",
    "Bamboo Shoot",
    "Beech",
    "Rose Bud",
    "Strawberry Shortcake",
    "Cactus",
    "Watermelon",
    "Serious",
    "Zigzag",
    "Herbivore",
    "Silence Whisper",
    "Carrot",
    "Cattail",
    "Hatsune",
    "Yam",
    "Potato Leaf",
    "Hot Butt",
    "Bone Sail, Rugged Sail",
    "Tri Spikes",
    "Green Thorns",
    "Indian Star",
    "Red Ear",
    "Croc",
    "Unko, Pinku Unko",
    "Scalpy Spear",
    "Cerastes",
    "Scalpy Spoon",
    "Incisor",
    "Bumpy",
    "Toothless Bite, Venom Bite",
    "Kotaro",
    "Razor Bite",
    "Tiny Turtle",
    "Wall Gecko, Escaped Gecko",
    "Iguana",
    "Tiny Dino",
    "Snake Jar",
    "Gila",
    "Grass Snake",
]
