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
    sort="Latest",
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
            "stages": 4,
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


# Snaker Jar -> December Suprise
# Granma´s Fan -> Omatsuri
# Fish Snack -> Maki
# Tiny Dino -> Fir Trunk
# Cottontail -> Sakura Cottontail
# Carrot -> Namek Carrot
# Koi -> Koinobori
# Cupid -> Origami
# Hermit -> Crystal Hermit
# Ronin -> Hasagi
# Revenge Arrow -> Hamaya
# Turnip -> Pink Turnip
# Indian Star -> Frozen Bucket
# Bone Sail -> Rugged Sail
# Shiitake -> Yakitori
# Garish Worm -> Candy Canes
# Babylonia -> Candy Babylonia
# Lagging -> Laggingggggg
# Little Branch -> Winter Branch
# Bamboo Shoot -> Golden Bamboo Shoot
# Pocky -> Umaibo
# Beech -> Yorishiro
# Shoal Star -> 5H04L-5T4R
# Imp -> Kendama
# Eggshell -> Golden Shell
# Cactus -> Santa's Gift
# Unko -> Pinku Unko
# Tiny turtle  -> Tiny Carrot, Dango
# Zigzag -> Rudolph
# Doubletalk -> Mr. Doubletalk
# Serious -> Humorless
# Piranha -> Geisha
# Mosquito -> Feasting Mosquito
# Cute Bunny -> Kawaii
# Lam -> Lam Handsome

# Sans mystic
parts = [
    "Koi",
    "Nimo",
    "Tadpole",
    "Ranchu",
    "Navaga",
    "Shrimp",
    "Cottontail",
    "Rice",
    "Shiba",
    "Hare",
    "Nut Cracker",
    "Gerbil",
    "Swallow",
    "Feather Fan",
    "The Last One",
    "Cloud",
    "Granma's Fan",
    "Post Fight",
    "Ant",
    "Twin Tail",
    "Fish Snack",
    "Gravel Ant",
    "Pupae",
    "Thorny Caterpillar",
    "Carrot",
    "Cattail",
    "Cottontail",
    "Hatsune",
    "Yam",
    "Potato Leaf",
    "Hot Butt",
    "Wall Gecko",
    "Iguana",
    "Tiny Dino",
    "Snake Jar",
    "Gila",
    "Grass Snake",
    "Hermit",
    "Blue Moon",
    "Goldfish",
    "Sponge",
    "Anemone",
    "Perch",
    "Ronin",
    "Hero",
    "Jaguar",
    "Risky Beast",
    "Timber",
    "Furball",
    "Balloon",
    "Cupid",
    "Raven",
    "Pigeon Post",
    "Kingfisher",
    "Tri Feather",
    "Snail Shell",
    "Garish Worm",
    "Buzz Buzz",
    "Sandal",
    "Scarab",
    "Spiky Wing",
    "Turnip",
    "Shiitake",
    "Bidens",
    "Watering Can",
    "Mint",
    "Pumpkin",
    "Bone Sail",
    "Tri Spikes",
    "Green Thorns",
    "Indian Star",
    "Red Ear",
    "Croc",
    "Babylonia",
    "Teal Shell",
    "Clamshell",
    "Anemone",
    "Oranda",
    "Shoal Star",
    "Little Branch",
    "Imp",
    "Merry",
    "Pocky",
    "Dual Blade",
    "Arco",
    "Eggshell",
    "Cuckoo",
    "Trump",
    "Kestrel",
    "Wing Horn",
    "Feather Spear",
    "Lagging",
    "Antenna",
    "Caterpillars",
    "Pliers",
    "Parasite",
    "Leaf Bug",
    "Bamboo Shoot",
    "Beech",
    "Rose Bud",
    "Strawberry Shortcake",
    "Cactus",
    "Watermelon",
    "Unko",
    "Scaly Spear",
    "Cerastes",
    "Scaly Spoon",
    "Incisor",
    "Bumpy",
    "Lam",
    "Catfish",
    "Risky Fish",
    "Piranha",
    "Nut Cracker",
    "Goda",
    "Axie Kiss",
    "Confident",
    "Doubletalk",
    "Peace Maker",
    "Hungry Bird",
    "Little Owl",
    "Mosquito",
    "Pincer",
    "Cute Bunny",
    "Square Teeth",
    "Serious",
    "Zigzag",
    "Herbivore",
    "Silence Whisper",
    "Toothless Bite",
    "Kotaro",
    "Razor Bite",
    "Tiny Turtle",
    "Dango",
]

tail_parts = [
    "Koi",
    "Koinobori",
    "Nimo",
    "Tadpole",
    "Ranchu",
    "Navaga",
    "Shrimp",
    "Cottontail",
    "Rice",
    "Shiba",
    "Hare",
    "Nut Cracker",
    "Gerbil",
    "Swallow",
    "Feather Fan",
    "The Last One",
    "Cloud",
    "Granma's Fan",
    "Omatsuri",
    "Post Fight",
    "Ant",
    "Twin Tail",
    "Fish Snack",
    "Maki",
    "Gravel Ant",
    "Pupae",
    "Thorny Caterpillar",
    "Carrot",
    "Namek Carrot",
    "Cattail",
    "Cottontail",
    "Sakura Cottontail",
    "Hatsune",
    "Yam",
    "Potato Leaf",
    "Hot Butt",
    "Wall Gecko",
    "Iguana",
    "Tiny Dino",
    "Fir Trunk",
    "Snake Jar",
    "December Surprise",
    "Gila",
    "Grass Snake",
]
back_parts = [
    "Hermit",
    "Crystal Hermit",
    "Blue Moon",
    "Goldfish",
    "Sponge",
    "Anemone",
    "Perch",
    "Ronin",
    "Hasagi",
    "Hero",
    "Jaguar",
    "Risky Beast",
    "Hamaya",
    "Timber",
    "Furball",
    "Balloon",
    "Cupid",
    "Origami",
    "Raven",
    "Pigeon Post",
    "Kingfisher",
    "Tri Feather",
    "Snail Shell",
    "Garish Worm",
    "Candy Canes",
    "Buzz Buzz",
    "Sandal",
    "Scarab",
    "Spiky Wing",
    "Turnip",
    "Pink Turnip",
    "Shiitake",
    "Yakitori",
    "Bidens",
    "Watering Can",
    "Mint",
    "Pumpkin",
    "Bone Sail",
    "Rugged Sail",
    "Tri Spikes",
    "Green Thorns",
    "Indian Star",
    "Frozen Bucket",
    "Red Ear",
    "Croc",
]
horn_parts = [
    "Babylonia",
    "Candy Babylonia",
    "Teal Shell",
    "Clamshell",
    "Anemone",
    "Oranda",
    "Shoal Star",
    "5H04L-5T4R",
    "Little Branch",
    "Winter Branch",
    "Imp",
    "Kendama",
    "Merry",
    "Pocky",
    "Umaibo",
    "Dual Blade",
    "Arco",
    "Eggshell",
    "Golden Shell",
    "Cuckoo",
    "Trump",
    "Kestrel",
    "Wing Horn",
    "Feather Spear",
    "Lagging",
    "Laggingggggg",
    "Antenna",
    "Caterpillars",
    "Pliers",
    "Parasite",
    "Leaf Bug",
    "Bamboo Shoot",
    "Golden Bamboo Shoot",
    "Beech",
    "Yorishiro",
    "Rose Bud",
    "Strawberry Shortcake",
    "Cactus",
    "Santa's Gift",
    "Watermelon",
    "Unko",
    "Pinku Unko",
    "Scaly Spear",
    "Cerastes",
    "Scaly Spoon",
    "Incisor",
    "Bumpy",
]
mouth_parts = [
    "Lam",
    "Lam Handsome",
    "Catfish",
    "Risky Fish",
    "Piranha",
    "Geisha",
    "Nut Cracker",
    "Goda",
    "Axie Kiss",
    "Confident",
    "Doubletalk",
    "Mr. Doubletalk",
    "Peace Maker",
    "Hungry Bird",
    "Little Owl",
    "Mosquito",
    "Feasting Mosquito",
    "Pincer",
    "Cute Bunny",
    "Kawaii",
    "Square Teeth",
    "Serious",
    "Humorless",
    "Zigzag",
    "Rudolph",
    "Herbivore",
    "Silence Whisper",
    "Toothless Bite",
    "Kotaro",
    "Razor Bite",
    "Tiny Turtle",
    "Tiny Carrot",
    "Dango",
]
