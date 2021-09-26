package main

import (
	"strconv"
)

// POST REQUESTS
func CreateBody(from int) RequestBody {
	body := RequestBody{}
	body.Query = query
	body.Variables.From = from
	body.Variables.Size = 100
	body.Variables.Sort = "Latest"
	body.Variables.AuctionType = "Sale"
	return body
}

var query string = `
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
`

type RequestBody struct {
	Query     string    `json:"query"`
	Variables Variables `json:"variables"`
}
type Variables struct {
	From        int      `json:"from"`
	Size        int      `json:"size"`
	Sort        string   `json:"sort"`
	AuctionType string   `json:"auctionType"`
	Owner       *string  `json:"owner"`
	Criteria    Criteria `json:"criteria"`
}
type Criteria struct {
	Region     *string   `json:"region"`
	Parts      *[]string `json:"parts"`
	BodyShapes *string   `json:"bodyShapes"`
	Classes    *[]string `json:"classes"`
	Stages     *int      `json:"stages"`
	NumMystic  *int      `json:"numMystic"`
	Pureness   *int      `json:"pureness"`
	Title      *string   `json:"title"`
	Breedable  *bool     `json:"breedable"`
	BreedCount *int      `json:"breedCount"`
	Hp         *int      `json:"hp"`
	Skill      *int      `json:"skill"`
	Speed      *int      `json:"speed"`
	Morale     *int      `json:"morale"`
}

// RAW RESPONSES
type JsonBlob struct {
	Data struct {
		Axies struct {
			Results []Axie `json:"results"`
		} `json:"axies"`
	} `json:"data"`
}
type Axie struct {
	Id         string     `json:"id,omitempty"`
	Class      string     `json:"class,omitempty"`
	BreedCount int        `json:"breedCount,omitempty"`
	Image      string     `json:"image,omitempty"`
	Auction    Auction    `json:"auction,omitempty"`
	BattleInfo BattleInfo `json:"battleInfo,omitempty"`
	Parts      *[6]Part   `json:"parts,omitempty"`
}
type Auction struct {
	CurrentPriceUSD string `json:"currentPriceUSD,omitempty"`
	CurrentPrice    string `json:"currentPrice,omitempty"`
}
type BattleInfo struct {
	Banned bool `json:"banned,omitempty"`
}
type Part struct {
	Name         string  `json:"name,omitempty"`
	Class        string  `json:"class,omitempty"`
	Type         string  `json:"type,omitempty"`
	SpecialGenes *string `json:"specialGenes,omitempty"`
}

// FORMAT RESPONSES FROM THE EXTERNAL API
// type MyError struct{}

func ExtractBatchInfo(blob JsonBlob) ([]AxieInfo, bool) {
	var Axies []AxieInfo
	if blob.Data.Axies.Results == nil {
		return Axies, true
	}
	for _, axie := range blob.Data.Axies.Results {
		axie_info := ExtractAxieInfo(axie)
		Axies = append(Axies, axie_info)
	}
	return Axies, false
}

func ExtractAxieInfo(ax Axie) AxieInfo {
	var axie AxieInfo
	axie.Id, _ = strconv.Atoi(ax.Id)
	axie.Class = ax.Class
	axie.Image = ax.Image
	axie.Price, _ = strconv.ParseFloat(ax.Auction.CurrentPriceUSD, 32)
	axie.BreedCount = ax.BreedCount
	axie.Eyes = ax.Parts[0].Name
	axie.Ears = ax.Parts[1].Name
	axie.Back = ax.Parts[2].Name
	axie.Mouth = ax.Parts[3].Name
	axie.Horn = ax.Parts[4].Name
	axie.Tail = ax.Parts[5].Name
	axie.EyesType = ax.Parts[0].Class
	axie.EarsType = ax.Parts[1].Class
	axie.BackType = ax.Parts[2].Class
	axie.MouthType = ax.Parts[3].Class
	axie.HornType = ax.Parts[4].Class
	axie.TailType = ax.Parts[5].Class
	return axie
}

type AxieInfo struct {
	Id         int
	Class      string
	Image      string
	Price      float64
	BreedCount int
	Eyes       string
	Ears       string
	Back       string
	Mouth      string
	Horn       string
	Tail       string
	EyesType   string
	EarsType   string
	BackType   string
	MouthType  string
	HornType   string
	TailType   string
}

// FORMAT PREDICTIONS FROM THE PYTHON SERVER
type AxieInfoEngineered struct {
	Id         int     `json:"Id"`
	Class      string  `json:"Class"`
	Image      string  `json:"Image"`
	Price      float64 `json:"Price"`
	Prediction float64 `json:"Prediction"`
	Eyes       string  `json:"Eyes"`
	Ears       string  `json:"Ears"`
	Back       string  `json:"Back"`
	Mouth      string  `json:"Mouth"`
	Horn       string  `json:"Horn"`
	Tail       string  `json:"Tail"`
	Hp         int     `json:"Hp"`
	Speed      int     `json:"Sp"`
	Skill      int     `json:"Sk"`
	Morale     int     `json:"Mr"`
}

// var mouth_to_card = map[string]string{
// 	"part1": "card1",
// 	"part2": "card2",
// }
// var back_to_card = map[string]string{
// 	"part1": "card1",
// 	"part2": "card2",
// }
// var horn_to_card = map[string]string{
// 	"part1": "card1",
// 	"part2": "card2",
// }
// var tail_to_card = map[string]string{
// 	"part1": "card1",
// 	"part2": "card2",
// }
