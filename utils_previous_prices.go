package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"time"
)

func get_price_history(nft AxieInfoEngineered) (bool, []OldPrice) {
	ids := GetIdsIdentifcalNfts(nft)
	var price_history []OldPrice
	var below_average = false
	for _, nft_id := range ids {
		transfer_history_nft := GetTransferHistory(nft_id)
		price_history = append(price_history, transfer_history_nft...)
		time.Sleep(time.Duration(rand.Intn(500)+500) * time.Millisecond) // Avoid getting blocked by the api if not using proxies
	}
	if (nft.PriceBy100)*0.01 < average(price_history) {
		below_average = true
	}
	return below_average, price_history
}

func average(prices []OldPrice) float64 {
	total := 0.0
	for _, price := range prices {
		total = total + price.Price
	}
	average := total / float64(len(prices))
	return average
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

func GetIdsIdentifcalNfts(nft AxieInfoEngineered) []int {
	var ids []int
	b, _ := json.Marshal(CreateBodyIdenticalNfts(nft))
	request, _ := http.NewRequest("POST", URL, bytes.NewBuffer(b))
	request.Header.Set("Content-Type", "application/json")
	response, err := external_api_client.Do(request)
	if err != nil {
		fmt.Printf("The HTTP request to the external API failed with error: %s\n", err)
		return ids
	}
	defer response.Body.Close()
	data, err := ioutil.ReadAll(response.Body)
	if err != nil {
		fmt.Printf("Error reading the response from the external api: %s\n", err)
		return ids
	}
	var result JsonBlob
	var bool_err bool
	json.Unmarshal([]byte(data), &result)
	ids, bool_err = ExtractBatchIds(result)
	if bool_err {
		fmt.Printf("Error. Empty responses from the market api\n")
		return ids
	}
	return ids
}
