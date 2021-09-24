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
var PRX string
var URL string = "https://axieinfinity.com/graphql-server-v2/graphql"

func main() {
	godotenv.Load()
	PRX = os.Getenv("URL")
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
		batch_results := feature_engineer_and_predict(batch, api_client)
		for _, nft := range batch_results {
			// nft_processed = feature_engineering(nft)
			if nft.Prediction > nft.Price+50 {
				notify_discord(nft, DISCORD_ID, DISCORD_TOKEN)
			}
		}
	}
}

// Sends the data in JSON format to a Python server through a Flask API.
// The feature engineering, model serving and predictions are done in Python, and the results are returned as JSON
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
	fmt.Println(string(results))
	var batch_results []AxieInfoEngineered
	json.Unmarshal([]byte(results), &batch_results)
	return batch_results
}

func get_data() {
	external_api_client := &http.Client{Timeout: time.Second * 10}
	var break_signal = make(chan bool)
	var wg sync.WaitGroup
	// Worker pool: n threads run on a loop calling get_data_batch while jobs arrive from post_queque
	wg.Add(NTHREADS)
	for i := 0; i < NTHREADS; i++ {
		go func() {
			for {
				i, ok := <-post_queque
				if !ok {
					fmt.Println("Empty requests queque -> Exiting thread.")
					wg.Done()
					return
				}
				get_data_batch(i, external_api_client)
				time.Sleep(time.Duration(rand.Intn(1)+1) * time.Second)
			}
		}()
	}
	// Adds jobs to post_queque on an infinite loop
	go func() {
		for {
			for i := 0; i < 10; i++ {
				post_queque <- i
			}
			_, ok := <-break_signal
			if ok {
				break
			}
		}
	}()
	// Press enter to break the infinite loop
	var input string
	fmt.Scanln(input)
	var signal bool
	break_signal <- signal
	// Waits for all the jobs that were added before breaking the loop to finish
	// close(post_queque)
	wg.Wait()
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
	fmt.Printf("Success")
	responses_queque <- batch
}
