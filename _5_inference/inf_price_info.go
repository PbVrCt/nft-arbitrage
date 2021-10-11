package main

import (
	"math/rand"
	"sync"
	"time"
)

func get_current_listings(nft AxieInfoEngineered, prices_ch chan []float64) {
	var body RequestBody = CreateBodyIdenticalNfts(nft, true, 7)
	data, _ := PostRequest(&body, external_api_client)
	prices := ParsePricesIdenticalNfts(data)
	prices_ch <- prices
}

func get_price_history(nft AxieInfoEngineered, full_history_ch chan PriceHistory) {
	// Get list of identical nfts not on sale
	var body RequestBody = CreateBodyIdenticalNfts(nft, false, 4)
	data, _ := PostRequest(&body, external_api_client)
	ids := ParseIdsIdenticalNfts(data)
	// Add the transfer history of each identical nft to a struct
	var history_ch = make(chan PriceHistory)
	var wg2 sync.WaitGroup
	wg2.Add(1)
	go func() {
		defer wg2.Done()
		var price_history PriceHistory
		for identical_nft_history := range history_ch {
			price_history = price_history.Append(identical_nft_history)
		}
		full_history_ch <- price_history
	}()
	// Get the transfer history of each nft
	var wg sync.WaitGroup
	wg.Add(len(ids))
	for _, nft_id := range ids {
		go func(nft_id int) {
			defer wg.Done()
			var bd RequestBodyTransferHistory = CreateBodyTransferHistory(nft_id)
			data, _ := PostRequest(&bd, external_api_client)
			transfer_history_nft := ParseTransferHistoryNft(data)
			history_ch <- transfer_history_nft
		}(nft_id)
		time.Sleep(time.Duration(rand.Intn(250)+250) * time.Millisecond) // To avoid getting blocked by the api if not using proxies
	}
	wg.Wait()
	close(history_ch)
	wg2.Wait()
}
