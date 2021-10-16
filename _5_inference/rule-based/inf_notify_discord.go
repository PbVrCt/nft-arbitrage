package main

import (
	"fmt"
	"sort"
	"strings"

	"github.com/bwmarrin/discordgo"
)

func notify_discord(nft AxieInfo, current_prices []float64, combo_prices []float64) {
	session, _ := discordgo.New()
	sort.Float64s(current_prices)
	sort.Float64s(combo_prices)
	embed := &discordgo.MessageEmbed{
		Title:       fmt.Sprint("ID: ", nft.Id),
		URL:         fmt.Sprint("https://marketplace.axieinfinity.com/axie/", nft.Id),
		Author:      &discordgo.MessageEmbedAuthor{},
		Color:       0x00ff00, // Green
		Description: "Precio USD:" + fmt.Sprintf("%.0f", nft.PriceUSD) + "\nPrecio: " + fmt.Sprintf("%.3f", nft.PriceBy100*0.01),
		Fields: []*discordgo.MessageEmbedField{
			{
				Name:   "Precios combo",
				Value:  strings.Trim(strings.Join(strings.Fields(fmt.Sprintf("%.3f", combo_prices)), "\n"), "[]"),
				Inline: true,
			},
			{
				Name:   "Precios",
				Value:  strings.Trim(strings.Join(strings.Fields(fmt.Sprintf("%.3f", current_prices)), "\n"), "[]"),
				Inline: true,
			},
			{
				Name:   nft.Class,
				Value:  fmt.Sprint(nft.Mouth, "\n", nft.Back, "\n", nft.Horn, "\n", nft.Tail),
				Inline: true,
			},
			{
				Name:   "BreedCount",
				Value:  fmt.Sprint(nft.BreedCount),
				Inline: true,
			},
		},
		Image: &discordgo.MessageEmbedImage{
			URL: nft.Image,
		},
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
