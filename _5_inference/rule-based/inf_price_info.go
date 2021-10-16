package main

func get_current_listings(nft AxieInfo, prices_ch chan []float64) {
	var body RequestBody = CreateBodySimilarNfts(nft, 7, map[string]string{})
	data, _ := PostRequest(&body, external_api_client)
	prices := ParsePricesSimilarNfts(data)
	prices_ch <- prices
}

func get_combo_prices(nft AxieInfo, combo map[string]string, combo_ch chan []float64) {
	var body RequestBody = CreateBodySimilarNfts(nft, 7, combo)
	data, _ := PostRequest(&body, external_api_client)
	prices := ParsePricesSimilarNfts(data)
	combo_ch <- prices
}
