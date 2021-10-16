package main

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"net/http"
	"sync"
	"time"
)

var post_queque = make(chan int, 10)             // Input channel
var responses_queque = make(chan []AxieInfo, 10) // Output channel
const NTHREADS = 1                               // Number of threads in the worker pool doing requests ; NTHREADS < cap(post_queque)
const MTHREADS = 20                              // Number of threads in the worker pool calling Python ; MTHREADS < cap(response_queque)
var URL string = "https://axieinfinity.com/graphql-server-v2/graphql"
var parts = get_parts_filters()
var bargains sync.Map

var external_api_client = &http.Client{Timeout: time.Second * 10}

// var prx_url, _ = url.Parse(PRX)
// var transport = &http.Transport{Proxy: http.ProxyURL(prx_url), TLSClientConfig: &tls.Config{InsecureSkipVerify: true}}
// var external_api_proxy_client = &http.Client{Transport: transport, Timeout: time.Second * 10}

func main() {
	LoadEnv()
	// go get_data(query_latest, 2)
	go get_data(query_brief_list, 100)
	go predict_on_batches()
	select {} // So the script runs until cancelled
}

func predict_on_batches() {
	// Worker pool: m threads take the different batches arriving from responses_queque and call Python for predictions
	for i := 0; i < MTHREADS; i++ {
		go func() {
			for {
				batch, ok := <-responses_queque
				fmt.Print("Batch\n")
				if ok {
					for _, nft := range batch {
						notify_if_rule(nft)
					}
				} else {
					fmt.Printf("Error getting data from go channel")
				}
				time.Sleep(time.Duration(rand.Intn(250)+250) * time.Millisecond) // To avoid getting blocked by the api if not using proxies
			}
		}()
	}
}

func avg(array []float64) float64 {
	result := 0.0
	for _, v := range array {
		result += v
	}
	return result / float64(len(array))
}

func notify_if_rule(nft AxieInfo) {
	in, combo := check_list(nft)
	if _, ok := bargains.Load(nft.Id); !ok && in {
		bargains.Store(nft.Id, true)
		var combo_ch = make(chan []float64)
		var prices_ch = make(chan []float64)
		go get_combo_prices(nft, combo, combo_ch)
		go get_current_listings(nft, prices_ch)
		combo_prices := <-combo_ch
		identical_prices := <-prices_ch
		if avg(combo_prices) > (nft.PriceBy100 * 0.01) {
			fmt.Print(nft.Id, "\n")
			go notify_discord(nft, identical_prices, combo_prices)
		}
	}
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
	var body RequestBody = CreateBodyFilterByParts(page*100, query, parts)
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
