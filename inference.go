package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"sync"
	"time"

	"github.com/joho/godotenv"
)

var post_queque = make(chan int, 50)             // Input channel
var responses_queque = make(chan []AxieInfo, 50) // Output channel
var batches []AxieInfo
var PRX string
var URL string = "https://axieinfinity.com/graphql-server-v2/graphql"

func main() {
	godotenv.Load()
	PRX = os.Getenv("URL")
	DISCORD_WEBHOOK_URL := os.Getenv("DISCORD_WEBHOOK_URL")
	// WEBHOOK := discord.Webhook.from_url(  // Replicate the python equivalent using the discordgo library
	// 	DISCORD_WEBHOOK_URL, adapter=discord.RequestsWebhookAdapter()
	// )

	go get_data()
	go predict_on_batches()
}

func predict_on_batches() {
	for {
		batch := <-responses_queque
		for _, nft := range batch {
			// feature_engineering(nft)    Will be Python embedded code or call to a Python api
			// predict(nft)				   Will be Python embedded code or call to a Python api
			// if prediction > price + 50 {
			// 	notify discord(prediction, nft)
			// }
		}
	}
}

func notify_discord(price_prediction int, nft AxieInfo) { // Replicate the python equivalent using the discordgo library
	// WEBHOOK.send(
	// 	f"""
	// 		https://marketplace.axieinfinity.com/axie/{id_}
	// 		price: {row['Price']} usd
	// 		price prediction: {row['Prediction']}
	// 		multiplier_score: {row['multiplier_score']}
	// 		card_score: {row['sum_card_score']}
	// 		combo_score: {row['sum_combo_score']}
	// 		build_score: {row['build_score']}
	// 		breedCount: {row['BreedCount']}
	// 		""",
	// 	embed=discord.Embed().set_image(url=row["Image"]),
	// )
}

func get_data() {
	var break_signal = make(chan bool)
	var wg sync.WaitGroup
	// Worker pool: n threads run on a loop calling get_data_batch while jobs arrive from post_queque
	const nthreads = 5 // nthreads < cap(post_queque)
	wg.Add(nthreads)
	for i := 0; i < nthreads; i++ {
		go func() {
			for {
				i, ok := <-post_queque
				if !ok {
					wg.Done()
					return
				}
				get_data_batch(i)
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

// Gets data from one post request
func get_data_batch(from int) {
	b, _ := json.Marshal(CreateBody(from))
	request, _ := http.NewRequest("POST", URL, bytes.NewBuffer(b))
	request.Header.Set("Content-Type", "application/json")
	client := &http.Client{Timeout: time.Second * 10}
	response, err := client.Do(request)
	if err != nil {
		fmt.Printf("The HTTP request failed with error %s\n", err)
		return
	}
	defer response.Body.Close()
	data, _ := ioutil.ReadAll(response.Body)
	var result JsonBlob
	json.Unmarshal([]byte(data), &result)
	batch := ExtractBatchInfo(result)
	responses_queque <- batch
}
