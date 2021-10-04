package main

import (
	"sync"
)

func price_info(nft AxieInfoEngineered) ([]float64, PriceHistory) {
	var prices_ch = make(chan []float64)
	var history_ch = make(chan PriceHistory)
	var full_history_ch = make(chan PriceHistory)
	go get_current_listings(nft, prices_ch)
	go get_price_history(nft, history_ch)
	go func() {
		var price_history PriceHistory
		for identical_nft_history := range history_ch {
			price_history = price_history.Append(identical_nft_history)
		}
		full_history_ch <- price_history
	}()
	prices := <-prices_ch
	price_history := <-full_history_ch
	return prices, price_history
}

func get_current_listings(nft AxieInfoEngineered, prices_ch chan []float64) {
	var body RequestBody = CreateBodyIdenticalNfts(nft, true)
	data := PostRequest(&body, external_api_client)
	prices := ParsePricesIdenticalNfts(data)
	prices_ch <- prices
}

func get_price_history(nft AxieInfoEngineered, history_ch chan PriceHistory) {
	var body RequestBody = CreateBodyIdenticalNfts(nft, false)
	data := PostRequest(&body, external_api_client)
	ids := ParseIdsIdenticalNfts(data)
	var wg sync.WaitGroup
	wg.Add(len(ids))
	for _, nft_id := range ids {
		go func(nft_id int) {
			defer wg.Done()
			var bd RequestBodyTransferHistory = CreateBodyTransferHistory(nft_id)
			data := PostRequest(&bd, external_api_client)
			transfer_history_nft := ParseTransferHistoryNft(data)
			history_ch <- transfer_history_nft
		}(nft_id)
		// time.Sleep(time.Duration(rand.Intn(500)+500) * time.Millisecond) // To avoid getting blocked by the api if not using proxies
	}
	wg.Wait()
	close(history_ch)
}
