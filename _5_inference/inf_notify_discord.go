package main

import (
	"fmt"
	"sort"
	"strings"

	"github.com/bwmarrin/discordgo"
)

func notify_discord(nft AxieInfoEngineered, current_prices []float64, price_history PriceHistory) {
	session, _ := discordgo.New()
	sort.Sort(SortByTimestamp(price_history))
	sort.Float64s(current_prices)
	embed := &discordgo.MessageEmbed{
		Title:       fmt.Sprint("ID: ", nft.Id),
		URL:         fmt.Sprint("https://marketplace.axieinfinity.com/axie/", nft.Id),
		Author:      &discordgo.MessageEmbedAuthor{},
		Color:       0x00ff00, // Green
		Description: "Precio USD:" + fmt.Sprintf("%.0f", nft.PriceUSD) + "\nPrecio: " + fmt.Sprintf("%.3f", nft.PriceBy100*0.01) + "\nPredicción:" + fmt.Sprintf("%.3f", nft.Prediction*0.01),
		Fields: []*discordgo.MessageEmbedField{
			{
				Name:   "Precios",
				Value:  strings.Trim(strings.Join(strings.Fields(fmt.Sprintf("%.3f", current_prices)), "\n"), "[]"),
				Inline: true,
			},
			{
				Name:   "Ventas similares",
				Value:  strings.Trim(strings.Join(strings.Fields(fmt.Sprintf("%.3f", price_history.Prices)), "\n"), "[]"),
				Inline: true,
			},
			{
				Name:   "Fechas",
				Value:  strings.Trim(strings.Join(strings.Fields(fmt.Sprint(price_history.Dates)), "\n"), "[]"),
				Inline: true,
			},
			{
				Name:   nft.Class,
				Value:  fmt.Sprint(nft.Mouth, "\n", nft.Back, "\n", nft.Horn, "\n", nft.Tail),
				Inline: true,
			},
			// {
			// 	Name:   "Stats",
			// 	Value:  fmt.Sprint("Hp: ", fmt.Sprintf("%.2f", nft.Hp), "\nSpeed: ", fmt.Sprintf("%.2f", nft.Speed), "\nSkill: ", fmt.Sprintf("%.2f", nft.Skill), "\nMorale: ", fmt.Sprintf("%.2f", nft.Morale)),
			// 	Inline: true,
			// },
			{
				Name:   "BreedCount",
				Value:  fmt.Sprint(nft.BreedCount),
				Inline: true,
			},
			{
				Name:   "Gene Quality",
				Value:  fmt.Sprintf("%.2f", nft.GeneQuality),
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

func notify_discord_no_history(nft AxieInfoEngineered, current_prices []float64) {
	session, _ := discordgo.New()
	sort.Float64s(current_prices)
	embed := &discordgo.MessageEmbed{
		Title:       fmt.Sprint("ID: ", nft.Id),
		URL:         fmt.Sprint("https://marketplace.axieinfinity.com/axie/", nft.Id),
		Author:      &discordgo.MessageEmbedAuthor{},
		Color:       0x00ff00, // Green
		Description: "Precio USD:" + fmt.Sprintf("%.0f", nft.PriceUSD) + "\nPrecio: " + fmt.Sprintf("%.3f", nft.PriceBy100*0.01) + "\nPredicción:" + fmt.Sprintf("%.0f", nft.Prediction*0.01),
		Fields: []*discordgo.MessageEmbedField{
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
			// {
			// 	Name:   "Stats",
			// 	Value:  fmt.Sprint("Hp: ", fmt.Sprintf("%.2f", nft.Hp), "\nSpeed: ", fmt.Sprintf("%.2f", nft.Speed), "\nSkill: ", fmt.Sprintf("%.2f", nft.Skill), "\nMorale: ", fmt.Sprintf("%.2f", nft.Morale)),
			// 	Inline: true,
			// },
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
