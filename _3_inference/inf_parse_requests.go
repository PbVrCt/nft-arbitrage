package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strconv"
	"strings"
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
  image
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
  image
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
func PostRequest(body interface{}, client *http.Client) []byte {
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
	}
	defer response.Body.Close()
	data, err := ioutil.ReadAll(response.Body)
	if err != nil {
		fmt.Printf("Error reading response from a request: %s\n", err)
	}
	return data
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
	axie.Id, _ = strconv.Atoi(ax.Id)
	axie.Class = ax.Class
	axie.Image = ax.Image
	price, _ := strconv.ParseFloat(ax.Auction.CurrentPrice, 32)
	axie.PriceBy100 = price * 1e-16
	axie.PriceUSD, _ = strconv.ParseFloat(ax.Auction.CurrentPriceUSD, 32)
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
	PriceBy100 float64
	PriceUSD   float64
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

// RESPONSE FORMAT FROM THE PYTHON SERVER
type AxieInfoEngineered struct {
	Id         int     `json:"Id"`
	Class      string  `json:"Class"`
	Image      string  `json:"Image"`
	PriceUSD   float64 `json:"PriceUSD"`
	PriceBy100 float64 `json:"PriceBy100"`
	Prediction float64 `json:"Prediction"`
	BreedCount int     `json:"BreedCount"`
	Eyes       string  `json:"Eyes"`
	Ears       string  `json:"Ears"`
	Back       string  `json:"Back"`
	Mouth      string  `json:"Mouth"`
	Horn       string  `json:"Horn"`
	Tail       string  `json:"Tail"`
}

// DEFINE REQUESTS IDENTICAL NFTS

func fmtPart(part string, part_category string) string {
	formatted := strings.ReplaceAll(part, " ", "-")
	formatted = strings.ToLower(formatted)
	formatted = part_category + "-" + formatted
	return formatted
}

func CreateBodyIdenticalNfts(nft AxieInfoEngineered, sale bool, size int) RequestBody {
	body := RequestBody{}
	body.Query = query_latest
	body.Variables.From = 0
	body.Variables.Size = size
	if sale {
		body.Variables.AuctionType = "Sale"
	} else {
		body.Variables.AuctionType = "All"
	}
	var sorting string = "PriceAsc"
	body.Variables.Sort = &sorting
	var parts = []string{fmtPart(nft.Back, "back"), fmtPart(nft.Mouth, "mouth"), fmtPart(nft.Horn, "horn"), fmtPart(nft.Tail, "tail")}
	body.Variables.Criteria.Parts = &parts
	var classes = []string{nft.Class}
	body.Variables.Criteria.Classes = &classes
	return body
}

// PARSE RESPONSES IDENTICAL NFTS

func ParseIdsIdenticalNfts(data []byte) []int {
	var result JsonBlob
	json.Unmarshal([]byte(data), &result)
	if result.Data.Axies.Results == nil {
		fmt.Printf("No similar nfts\n")
	}
	var ids []int
	for _, axie := range result.Data.Axies.Results {
		id, _ := strconv.Atoi(axie.Id)
		ids = append(ids, id)
	}
	return ids
}

func ParsePricesIdenticalNfts(data []byte) []float64 {
	var result JsonBlob
	json.Unmarshal([]byte(data), &result)
	if result.Data.Axies.Results == nil {
		fmt.Printf("No similar nfts\n")
	}
	var prices []float64
	for _, axie := range result.Data.Axies.Results {
		price, _ := strconv.ParseFloat(axie.Auction.CurrentPrice, 64)
		prices = append(prices, price*1e-18)
	}
	return prices
}

// DEFINE REQUESTS TRANSFER HISTORY

func CreateBodyTransferHistory(id int) RequestBodyTransferHistory {
	body := RequestBodyTransferHistory{}
	body.Query = query_transfer_history
	body.Variables.AxieId = id
	body.Variables.From = 0
	body.Variables.Size = 2
	return body
}

var query_transfer_history string = `
query GetAxieTransferHistory($axieId: ID!, $from: Int!, $size: Int!) {
	axie(axieId: $axieId) {
		id
		transferHistory(from: $from, size: $size) {
		...TransferRecords
		}
	}
	}
	
	fragment TransferRecords on TransferRecords {
	total
	results {
		from
		to
		timestamp
		txHash
		withPrice
	}
	}
`

type RequestBodyTransferHistory struct {
	Query     string                   `json:"query"`
	Variables VariablesTransferHistory `json:"variables"`
}
type VariablesTransferHistory struct {
	AxieId int `json:"axieId"`
	From   int `json:"from"`
	Size   int `json:"size"`
}

// RESPONSES FORMAT TRANSFER HISTORY

type JsonBlobTransferHistory struct {
	Data struct {
		Axie struct {
			Id              string          `json:"id"`
			TransferHistory TransferHistory `json:"transferHistory"`
		} `json:"axie"`
	} `json:"data"`
}
type TransferHistory struct {
	Total   int      `json:"total"`
	Results []Result `json:"results"`
}
type Result struct {
	From      string `json:"from"`
	To        string `json:"to"`
	Timestamp int    `json:"timestamp"`
	TxHash    string `json:"txHash"`
	WithPrice string `json:"withPrice"`
}

// PARSE RESPONSES TRANSFER HISTORY

func ParseTransferHistoryNft(data []byte) PriceHistory {
	var result JsonBlobTransferHistory
	json.Unmarshal([]byte(data), &result)
	if result.Data.Axie.TransferHistory.Results == nil {
		fmt.Printf("No transfer history\n")
	}
	var history PriceHistory
	for _, transfer := range result.Data.Axie.TransferHistory.Results {
		price, timestamp, date := OneTransfer(transfer)
		history.Prices = append(history.Prices, price)
		history.Dates = append(history.Dates, date)
		history.Timestamps = append(history.Timestamps, timestamp)
		history.Ids = append(history.Ids, result.Data.Axie.Id)
	}
	return history
}

func OneTransfer(result Result) (float64, time.Time, string) {
	price_value, _ := strconv.ParseFloat(result.WithPrice, 64)
	unix := time.Unix(int64(result.Timestamp), 0)
	date := strconv.FormatInt(int64(unix.Day()), 10) + "/" + strconv.FormatInt(int64((unix.Month())), 10) + "/" + strconv.FormatInt(int64(unix.Year()), 10)
	return price_value * 1e-18, unix, date
}

type PriceHistory struct {
	Prices     []float64
	Timestamps []time.Time
	Dates      []string
	Ids        []string
}

// APPEND TRANSFER HISTORY

func (h *PriceHistory) Append(item PriceHistory) PriceHistory {
	h.Prices = append(h.Prices, item.Prices...)
	h.Dates = append(h.Dates, item.Dates...)
	h.Timestamps = append(h.Timestamps, item.Timestamps...)
	h.Ids = append(h.Ids, item.Ids...)
	return *h
}

// SORT TRANSFER HISTORY

type SortByTimestamp PriceHistory

func (sbo SortByTimestamp) Len() int {
	return len(sbo.Prices)
}

func (sbo SortByTimestamp) Swap(i, j int) {
	sbo.Prices[i], sbo.Prices[j] = sbo.Prices[j], sbo.Prices[i]
	sbo.Dates[i], sbo.Dates[j] = sbo.Dates[j], sbo.Dates[i]
	sbo.Ids[i], sbo.Ids[j] = sbo.Ids[j], sbo.Ids[i]
	sbo.Timestamps[i], sbo.Timestamps[j] = sbo.Timestamps[j], sbo.Timestamps[i]
}

func (sbo SortByTimestamp) Less(i, j int) bool {
	return sbo.Timestamps[i].After(sbo.Timestamps[j])
}

type SortByPrice PriceHistory

func (sbo SortByPrice) Len() int {
	return len(sbo.Prices)
}

func (sbo SortByPrice) Swap(i, j int) {
	sbo.Prices[i], sbo.Prices[j] = sbo.Prices[j], sbo.Prices[i]
	sbo.Dates[i], sbo.Dates[j] = sbo.Dates[j], sbo.Dates[i]
	sbo.Ids[i], sbo.Ids[j] = sbo.Ids[j], sbo.Ids[i]
	sbo.Timestamps[i], sbo.Timestamps[j] = sbo.Timestamps[j], sbo.Timestamps[i]
}

func (sbo SortByPrice) Less(i, j int) bool {
	return sbo.Prices[i] < sbo.Prices[j]
}
