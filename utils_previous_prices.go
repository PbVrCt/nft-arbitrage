package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"sort"
	"time"
)

func get_current_listings(nft AxieInfoEngineered) ([]float64, float64) {
	data := PostRequestIdentifcalNfts(nft, true)
	prices := GetPricesIdenticalNfts(data)
	sort.Float64s(prices)
	if len(prices) > 1 {
		return prices, prices[1]
	} else {
		return prices, 0.0
	}
}

func get_price_history(nft AxieInfoEngineered) []OldPrice {
	data := PostRequestIdentifcalNfts(nft, false)
	ids := GetIdsIdenticalNfts(data)
	var price_history []OldPrice
	for _, nft_id := range ids {
		transfer_history_nft := GetTransferHistory(nft_id)
		price_history = append(price_history, transfer_history_nft...)
		time.Sleep(time.Duration(rand.Intn(500)+500) * time.Millisecond) // To avoid getting blocked by the api if not using proxies
	}
	return price_history
}

func GetTransferHistory(nft_id int) []OldPrice {
	var history []OldPrice
	b, _ := json.Marshal(CreateBodyTransferHistory(nft_id))

	request, _ := http.NewRequest("POST", URL, bytes.NewBuffer(b))
	request.Header.Set("Content-Type", "application/json")
	response, err := external_api_client.Do(request)
	if err != nil {
		fmt.Printf("The HTTP request to the external API failed with error: %s\n", err)
		return history
	}
	defer response.Body.Close()
	data, err := ioutil.ReadAll(response.Body)

	// fmt.Println(string(data))

	if err != nil {
		fmt.Printf("Error reading the response from the external api: %s\n", err)
		return history
	}
	var result JsonBlobTransferHistory
	var bool_err bool
	json.Unmarshal([]byte(data), &result)

	// prettyJSON, err := json.MarshalIndent(result, "", "    ")
	// if err != nil {
	// 	println("Failed to generate json")
	// }
	// fmt.Printf("%s\n", string(prettyJSON))

	history, bool_err = ExtractBatchTransferHistory(result)
	if bool_err {
		fmt.Printf("Error. Empty response from the market api\n")
	}
	return history
}

func PostRequestIdentifcalNfts(nft AxieInfoEngineered, sale bool) []byte {
	b, _ := json.Marshal(CreateBodyIdenticalNfts(nft, sale))
	request, _ := http.NewRequest("POST", URL, bytes.NewBuffer(b))
	request.Header.Set("Content-Type", "application/json")
	response, err := external_api_client.Do(request)
	if err != nil {
		fmt.Printf("The HTTP request to the external API failed with error: %s\n", err)
	}
	defer response.Body.Close()
	data, err := ioutil.ReadAll(response.Body)
	if err != nil {
		fmt.Printf("Error reading the response from the external api: %s\n", err)
	}
	return data
}
func GetIdsIdenticalNfts(data []byte) []int {
	var result JsonBlob
	json.Unmarshal([]byte(data), &result)
	ids, bool_err := ExtractBatchIds(result)
	if bool_err {
		fmt.Printf("Error. Empty responses from the market api\n")
		return ids
	}
	return ids
}

func GetPricesIdenticalNfts(data []byte) []float64 {
	var result JsonBlob
	json.Unmarshal([]byte(data), &result)
	prices, bool_err := ExtractBatchPrices(result)
	if bool_err {
		fmt.Printf("Error. Empty responses from the market api\n")
		return prices
	}
	return prices
}
