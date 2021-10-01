package main

import (
	"fmt"
	"sort"
	"strings"
	"time"

	"github.com/bwmarrin/discordgo"
)

func notify_discord(nft AxieInfoEngineered, old_prices []OldPrice) {
	session, _ := discordgo.New()

	var prices []string
	var dates []string
	var timestamps []time.Time
	for _, p := range old_prices {
		prices = append(prices, fmt.Sprintf("%.3f", p.Price))
		dates = append(dates, p.Date)
		timestamps = append(timestamps, p.Timestamp)
	}
	price_history := PriceHistorySlices{prices: prices, dates: dates, timestamps: timestamps}
	sort.Sort(SortByTimestamp(price_history))

	embed := &discordgo.MessageEmbed{
		Title:       fmt.Sprint("ID: ", nft.Id),
		URL:         fmt.Sprint("https://marketplace.axieinfinity.com/axie/", nft.Id),
		Author:      &discordgo.MessageEmbedAuthor{},
		Color:       0x00ff00, // Green
		Description: "Precio:" + fmt.Sprintf("%.0f", nft.PriceUSD) + "\nPredicción:" + fmt.Sprintf("%.0f", nft.Prediction) + "\nEth: " + fmt.Sprintf("%.3f", nft.PriceBy100*0.01),
		Fields: []*discordgo.MessageEmbedField{
			{
				Name:   nft.Class,
				Value:  fmt.Sprint(nft.Mouth, "\n", nft.Back, "\n", nft.Horn, "\n", nft.Tail),
				Inline: true,
			},
			{
				Name:   "Stats",
				Value:  fmt.Sprint("Hp: ", fmt.Sprintf("%.2f", nft.Hp), "\nSpeed: ", fmt.Sprintf("%.2f", nft.Speed), "\nSkill: ", fmt.Sprintf("%.2f", nft.Skill), "\nMorale: ", fmt.Sprintf("%.2f", nft.Morale)),
				Inline: true,
			},
			{
				Name:   "BreedCount",
				Value:  fmt.Sprint(nft.BreedCount),
				Inline: true,
			},
			{
				Name:   "Precios previos",
				Value:  fmt.Sprintln(strings.Join(price_history.prices, "\n")),
				Inline: true,
			},
			{
				Name:   "Fechas",
				Value:  fmt.Sprintln(strings.Join(price_history.dates, "\n")),
				Inline: true,
			},
		},
		Image: &discordgo.MessageEmbedImage{
			URL: nft.Image,
		},
		// Thumbnail: &discordgo.MessageEmbedThumbnail{
		// 	URL:    nft.Image,
		// 	Width:  1280,
		// 	Height: 960,
		// },
	}
	embeds := []*discordgo.MessageEmbed{}
	embeds = append(embeds, embed)
	_, err := session.WebhookExecute(DISCORD_ID, DISCORD_TOKEN, true, &discordgo.WebhookParams{
		// Content: "",
		Embeds: embeds,
	})
	if err != nil {
		fmt.Println("Webhook error:")
		fmt.Println(err)
	}
}

type PriceHistorySlices struct {
	prices     []string
	dates      []string
	timestamps []time.Time
}

type SortByTimestamp PriceHistorySlices

func (sbo SortByTimestamp) Len() int {
	return len(sbo.prices)
}

func (sbo SortByTimestamp) Swap(i, j int) {
	sbo.prices[i], sbo.prices[j] = sbo.prices[j], sbo.prices[i]
	sbo.dates[i], sbo.dates[j] = sbo.dates[j], sbo.dates[i]
	sbo.timestamps[i], sbo.timestamps[j] = sbo.timestamps[j], sbo.timestamps[i]
}

func (sbo SortByTimestamp) Less(i, j int) bool {
	return sbo.timestamps[i].After(sbo.timestamps[j])
}
