package main

// Check if nft is inside list of combos

func check_list(nft AxieInfo) (bool, map[string]string) {
	for _, combo := range filters[nft.Class] {
		if combo["back"] == nft.Back && combo["mouth"] == nft.Mouth && combo["horn"] == nft.Horn && combo["tail"] == nft.Tail {
			return true, combo
		}
	}
	for _, combo := range filters_b_m_h[nft.Class] {
		if combo["back"] == nft.Back && combo["mouth"] == nft.Mouth && combo["horn"] == nft.Horn {
			return true, combo
		}
	}
	for _, combo := range filters_b_m_t[nft.Class] {
		if combo["back"] == nft.Back && combo["mouth"] == nft.Mouth && combo["tail"] == nft.Tail {
			return true, combo
		}
	}
	for _, combo := range filters_b_h_t[nft.Class] {
		if combo["back"] == nft.Back && combo["horn"] == nft.Horn && combo["tail"] == nft.Tail {
			return true, combo
		}
	}
	for _, combo := range filters_m_h_t[nft.Class] {
		if combo["mouth"] == nft.Mouth && combo["horn"] == nft.Horn && combo["tail"] == nft.Tail {
			return true, combo
		}
	}
	return false, map[string]string{}
}

var filters = map[string][]map[string]string{
	"Plant": {},
	"Aquatic": {
		{"back": "Goldfish", "mouth": "Risky Fish", "horn": "Shoal Star", "tail": "Nimo"},
		{"back": "Goldfish", "mouth": "Risky Fish", "horn": "Shoal Star", "tail": "Koi"},
		{"back": "Anemone", "mouth": "Lam", "horn": "Anemone", "tail": "Nimo"},
	},
	"Bird": {
		{"back": "Pigeon Post", "mouth": "Doubletalk", "horn": "Kestrel", "tail": "Post Fight"},
		{"back": "Ronin", "mouth": "Doubletalk", "horn": "Kestrel", "tail": "Post Fight"},
	},
	"Beast": {
		{"back": "Ronin", "mouth": "Nut Cracker", "horn": "Imp", "tail": "Nut Cracker"},
		{"back": "Ronin", "mouth": "Axie Kiss", "horn": "Dual Blade", "tail": "Cottontail"},
	},
	"Dusk": {{"back": "Snail Shell", "mouth": "Tiny Turtle", "horn": "Lagging", "tail": "Thorny Caterpillar"}},
	"Bug": {
		{"back": "SnailShell", "mouth": "Pincer", "horn": "Parasite", "tail": "Gravel Ant"},
		{"back": "Snail Shell", "mouth": "Pincer", "horn": "Parasite", "tail": "Fish Snack"},
	},
	"Mech": {
		{"back": "Ronin", "mouth": "Nut Cracker", "horn": "Imp", "tail": "Nut Cracker"},
	},
	"Reptile": {},
	"Dawn":    {},
}

var filters_b_m_h = map[string][]map[string]string{
	"Plant":   {},
	"Aquatic": {},
	"Bird":    {},
	"Beast":   {},
	"Dusk":    {},
	"Bug":     {{"back": "Garish Worm", "mouth": "Cute Bunny", "horn": "Antenna"}},
	"Mech":    {},
	"Reptile": {},
	"Dawn":    {},
}

var filters_b_m_t = map[string][]map[string]string{
	"Plant":   {{"back": "Pumpkin", "mouth": "Serious", "tail": "Carrot"}},
	"Aquatic": {},
	"Bird":    {},
	"Beast":   {},
	"Dusk":    {},
	"Bug":     {},
	"Mech":    {},
	"Reptile": {},
	"Dawn":    {},
}

var filters_b_h_t = map[string][]map[string]string{
	"Plant":   {},
	"Aquatic": {},
	"Bird":    {},
	"Beast":   {},
	"Dusk":    {},
	"Bug":     {},
	"Mech":    {},
	"Reptile": {},
	"Dawn":    {},
}

var filters_m_h_t = map[string][]map[string]string{
	"Plant":   {},
	"Aquatic": {},
	"Bird":    {},
	"Beast":   {},
	"Dusk":    {},
	"Bug":     {{"mouth": "Cute Bunny", "horn": "Antenna", "tail": "Fish Snack"}},
	"Mech":    {},
	"Reptile": {},
	"Dawn":    {},
}

// Get parts that make up the combos

type NftPart struct {
	Parttype string
	Part     string
}

func get_parts_filters() []NftPart {
	var parts []NftPart
	for _, filter := range []map[string][]map[string]string{filters, filters_b_m_h, filters_b_m_t, filters_b_h_t, filters_m_h_t} {
		for _, combos := range filter {
			for _, combo := range combos {
				for part_type, part := range combo {
					parts = append(parts, NftPart{part_type, part})
				}
			}
		}
	}
	parts = removeDuplicateNftParts(parts)
	return parts
}

func removeDuplicateNftParts(NftPartSlice []NftPart) []NftPart {
	allKeys := make(map[NftPart]bool)
	list := []NftPart{}
	for _, item := range NftPartSlice {
		if _, value := allKeys[item]; !value {
			allKeys[item] = true
			list = append(list, item)
		}
	}
	return list
}
