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

var post_queque = make(chan int, 10)             // Input channel
var responses_queque = make(chan []AxieInfo, 10) // Output channel
const NTHREADS = 1                               // Number of threads in the worker pool doing requests ; NTHREADS < cap(post_queque)
const MTHREADS = 20                              // Number of threads in the worker pool calling Python ; MTHREADS < cap(response_queque)
var URL string = "https://axieinfinity.com/graphql-server-v2/graphql"
var bargains = make(map[int]bool)

var external_api_client = &http.Client{Timeout: time.Second * 10}
var python_api_client = &http.Client{Timeout: time.Second * 10}

// var prx_url, _ = url.Parse(PRX)
// var transport = &http.Transport{Proxy: http.ProxyURL(prx_url), TLSClientConfig: &tls.Config{InsecureSkipVerify: true}}
// var external_api_proxy_client = &http.Client{Transport: transport, Timeout: time.Second * 10}

func main() {
	LoadEnv()
	go get_data(query_latest, 2)
	// go get_data(query_brief_list, 100)
	go predict_on_batches()
	select {} // So the script runs until cancelled
}

func predict_on_batches() {
	// Worker pool: m threads take the different batches arriving from responses_queque and call Python for predictions
	for i := 0; i < MTHREADS; i++ {
		go func() {
			for {
				batch, ok := <-responses_queque
				if ok {
					batch_results := feature_engineer_and_predict(batch)
					for _, nft := range batch_results {
						notify_if_cheap(nft)
					}
				} else {
					fmt.Printf("Error getting data from go channel")
				}
				time.Sleep(time.Duration(rand.Intn(250)+250) * time.Millisecond) // To avoid getting blocked by the api if not using proxies
			}
		}()
	}
}

// 2 step filer: 1) price vs ML price prediction 2) price vs market prices
func notify_if_cheap(nft AxieInfoEngineered) {
	if _, ok := bargains[nft.Id]; !ok && (nft.Prediction*0.01) > (nft.PriceBy100*0.01)*1.5 && nft.PriceUSD > 50 {
		bargains[nft.Id] = true
		start := time.Now()
		var prices_ch = make(chan []float64)
		var history_ch = make(chan PriceHistory)
		go get_current_listings(nft, prices_ch) // 1 request
		go get_price_history(nft, history_ch)   // 1 -> 5 requests
		current_prices := <-prices_ch
		price_history := <-history_ch
		elapsed := time.Since(start)
		fmt.Printf("Price_info took: %s \n", elapsed)
		sort.Float64s(current_prices)
		sort.Sort(SortByPrice(price_history))
		switch {
		case len(current_prices) > 1:
			if current_prices[1] > 0.02+(nft.PriceBy100*0.01) {
				go notify_discord(nft, current_prices, price_history)
			}
		case len(price_history.Prices) > 0:
			last_sale_timecutoff, _ := time.Parse("2006-01-02", "2021-09-15")
			if price_history.Prices[0] > (nft.PriceBy100*0.01) && price_history.Timestamps[0].After(last_sale_timecutoff) {
				go notify_discord(nft, current_prices, price_history)
			}
		}
	}
}

// Sends the data in JSON format to a Python server through a Flask API. Then,
// the feature engineering, model serving and predictions are done in Python, and the results are returned to Go
func feature_engineer_and_predict(batch []AxieInfo) []AxieInfoEngineered {
	b, _ := json.Marshal(batch)
	request, _ := http.NewRequest("POST", "http://localhost:5000/api/predict", bytes.NewBuffer(b))
	request.Header.Set("Content-Type", "application/json")
	response, err := python_api_client.Do(request)
	if err != nil {
		fmt.Printf("The HTTP request to the Python server failed with error: %s\n", err)
		return nil
	}
	defer response.Body.Close()
	results, _ := ioutil.ReadAll(response.Body)
	var batch_results []AxieInfoEngineered
	json.Unmarshal([]byte(results), &batch_results)
	if len(batch_results) == 0 {
		fmt.Print("Empty/bad respone from the Python api")
	} else {
		fmt.Printf("\n%v\n", batch_results[0].Id)
	}
	return batch_results
}

func get_data(query string, pages_to_scan int) {
	// Adds jobs to post_queque on an infinite loop
	go func() {
		for {
			for i := 0; i < pages_to_scan; i++ {
				post_queque <- i
			}
		}
	}()
	// Worker pool: Wihle jobs arrive from post_queque, n threads run on a loop calling get_data_batch
	for i := 0; i < NTHREADS; i++ {
		go func() {
			for {
				i, ok := <-post_queque
				if !ok {
					fmt.Printf("Exiting thread")
					return
				}
				get_data_batch(i, query)
			}
		}()
	}
}

// Gets data from a single post request to the external API
func get_data_batch(page int, query string) {
	var body RequestBody = CreateBody(page*100, query)
	data, err := PostRequest(&body, external_api_client)
	if err != nil {
		return
	}
	var result JsonBlob
	var batch []AxieInfo
	json.Unmarshal([]byte(data), &result)
	batch = ExtractBatchInfo(result)
	if cap(batch) < 128 {
		fmt.Printf("Response from the market api doesn't have the adeaquate length\n")
		return
	}
	responses_queque <- batch
}
