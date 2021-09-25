package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"math/rand"
	"net/http"
	"os"
	"sync"
	"time"

	"github.com/joho/godotenv"
)

var post_queque = make(chan int, 50)             // Input channel
var responses_queque = make(chan []AxieInfo, 50) // Output channel
const NTHREADS = 1                               // Number of threads in the worker pool doing requests ; NTHREADS < cap(post_queque)
const PAGES_TO_SCAN = 10                         // Each page shows 100 nfts
var URL string = "https://axieinfinity.com/graphql-server-v2/graphql"
var bargains = make(map[int]bool)

func main() {
	godotenv.Load()
	// PRX = os.Getenv("URL")
	DISCORD_ID := os.Getenv("DISCORD_WEBHOOK_ID")
	DISCORD_TOKEN := os.Getenv("DISCORD_WEBHOOK_TOKEN")
	go get_data()
	go predict_on_batches(DISCORD_ID, DISCORD_TOKEN)
	select {} // So the script runs until cancelled
}

func predict_on_batches(DISCORD_ID string, DISCORD_TOKEN string) {
	api_client := &http.Client{Timeout: time.Second * 10}
	for {
		batch := <-responses_queque
		go func() {
			batch_results := feature_engineer_and_predict(batch, api_client) // Takes 0.5s/batch. Keep an eye on the Python server for concurrent requests causing problems
			bargain_counter := 0
			for _, nft := range batch_results {
				if _, ok := bargains[nft.Id]; !ok && nft.Prediction > nft.Price+200 && nft.Price > 50 {
					bargains[nft.Id] = true
					bargain_counter++
					go notify_discord(nft, DISCORD_ID, DISCORD_TOKEN)
				}
			}
			fmt.Printf("Bargains: " + fmt.Sprint(bargain_counter) + "/100\n")
		}()
	}
}

// Sends the data in JSON format to a Python server through a Flask API. Then,
// the feature engineering, model serving and predictions are done in Python, and the results are returned as a JSON
func feature_engineer_and_predict(batch []AxieInfo, api_client *http.Client) []AxieInfoEngineered {
	b, _ := json.Marshal(batch)
	request, _ := http.NewRequest("POST", "http://localhost:5000/api/predict", bytes.NewBuffer(b))
	request.Header.Set("Content-Type", "application/json")
	response, err := api_client.Do(request)
	if err != nil {
		fmt.Printf("The HTTP request to the Python server failed with error: %s\n", err)
		return nil
	}
	defer response.Body.Close()
	results, _ := ioutil.ReadAll(response.Body)
	var batch_results []AxieInfoEngineered
	json.Unmarshal([]byte(results), &batch_results)
	return batch_results
}

func get_data() {
	external_api_client := &http.Client{Timeout: time.Second * 10}
	var wg sync.WaitGroup
	// Adds jobs to post_queque on an infinite loop
	go func() {
		for {
			for i := 0; i < PAGES_TO_SCAN; i++ {
				post_queque <- i
			}
		}
	}()
	// Worker pool: n threads run on a loop calling get_data_batch while jobs arrive from post_queque
	wg.Add(NTHREADS)
	for i := 0; i < NTHREADS; i++ {
		go func() {
			for {
				i, ok := <-post_queque
				if !ok {
					fmt.Printf("Exiting thread")
					wg.Done()
					return
				}
				get_data_batch(i, external_api_client)
				time.Sleep(time.Duration(rand.Intn(1)+1) * time.Second)
			}
		}()
	}
	wg.Wait() // For now does nothing because the loop is infinite
}

// Gets data from a single post request to the external API
func get_data_batch(from int, external_api_client *http.Client) {
	b, _ := json.Marshal(CreateBody(from))
	request, _ := http.NewRequest("POST", URL, bytes.NewBuffer(b))
	request.Header.Set("Content-Type", "application/json")
	response, err := external_api_client.Do(request)
	if err != nil {
		fmt.Printf("The HTTP request to the external API failed with error: %s\n", err)
		return
	}
	defer response.Body.Close()
	data, err := ioutil.ReadAll(response.Body)
	if err != nil {
		fmt.Printf("Error reading the response from the external api: %s\n", err)
		return
	}
	var result JsonBlob
	json.Unmarshal([]byte(data), &result)
	batch := ExtractBatchInfo(result)
	responses_queque <- batch
}
