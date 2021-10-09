package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"strconv"
	"time"
)

// DEFINE REQUESTS
func CreateBody(from int, query string) RequestBody {
	body := RequestBody{}
	body.Query = query
	body.Variables.From = from
	body.Variables.Size = 100
	var sorting string = "Latest"
	body.Variables.Sort = &sorting
	body.Variables.AuctionType = "Sale"
	var Stages int = 4
	body.Variables.Criteria.Stages = &Stages
	return body
}

var query_latest string = `
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
  genes
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

var query_brief_list string = `
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
  genes
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
	Sort        *string  `json:"sort"`
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
	BreedCount *[]int    `json:"breedCount"`
	Hp         *int      `json:"hp"`
	Skill      *int      `json:"skill"`
	Speed      *int      `json:"speed"`
	Morale     *int      `json:"morale"`
}

// DO REQUESTS
func PostRequest(body interface{}, client *http.Client) ([]byte, error) {
	b, _ := json.Marshal(body)
	request, _ := http.NewRequest("POST", URL, bytes.NewBuffer(b))

	request.Header.Set("Content-Type", "application/json")
	parseFormErr := request.ParseForm()
	if parseFormErr != nil {
		fmt.Println("Error defining the request: ", parseFormErr)
	}
	response, err := client.Do(request)
	if err != nil {
		fmt.Printf("The HTTP request failed with error: %s\n", err)
		return []byte(""), errors.New("failed request")
	}
	defer response.Body.Close()
	data, err := ioutil.ReadAll(response.Body)
	if err != nil {
		fmt.Printf("Error reading response from a request: %s\n", err)
	}
	return data, nil
}

// RESPONSES FORMAT
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
	Genes      string     `json:"genes,omitempty"`
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

// PARSE RESPONSES

func ExtractBatchInfo(blob JsonBlob) []AxieInfo {
	var Axies []AxieInfo
	for _, axie := range blob.Data.Axies.Results {
		axie_info := ExtractAxieInfo(axie)
		Axies = append(Axies, axie_info)
	}
	return Axies
}

func ExtractAxieInfo(ax Axie) AxieInfo {
	var axie AxieInfo
	axie.Date = time.Now().Format(time.RFC3339)
	axie.Id, _ = strconv.Atoi(ax.Id)
	axie.Class = ax.Class
	price, _ := strconv.ParseFloat(ax.Auction.CurrentPrice, 32)
	axie.PriceBy100 = price * 1e-16
	axie.PriceUSD, _ = strconv.ParseFloat(ax.Auction.CurrentPriceUSD, 32)
	axie.BreedCount = ax.BreedCount
	axie.Genes = ax.Genes
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
	Date       string
	Id         int
	Class      string
	PriceBy100 float64
	PriceUSD   float64
	BreedCount int
	Genes      string
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
