package main

import (
	"fmt"

	"github.com/bwmarrin/discordgo"
)

func notify_discord(nft AxieInfoEngineered, webhook_id string, webhook_token string) {
	session, _ := discordgo.New()
	embed := &discordgo.MessageEmbed{
		Title:       "Link",
		URL:         "https://marketplace.axieinfinity.com/axie/6073615",
		Author:      &discordgo.MessageEmbedAuthor{},
		Color:       0x00ff00, // Green
		Description: "Precio: 100\nPredicción:" + fmt.Sprint(nft.Price),
		Fields: []*discordgo.MessageEmbedField{
			&discordgo.MessageEmbedField{
				Name:   "Planta",
				Value:  "Vegetal Bite\nPrickly Trap\nSwift Escape\nCarrot Hammer",
				Inline: true,
			},
			&discordgo.MessageEmbedField{
				Name:   "Stats",
				Value:  "HP: 40\nSp: 40\nSk: 40\nMr: 40",
				Inline: true,
			},
		},
		Image: &discordgo.MessageEmbedImage{
			URL: "https://storage.googleapis.com/assets.axieinfinity.com/axies/6073615/axie/axie-full-transparent.png",
		},
		// Thumbnail: &discordgo.MessageEmbedThumbnail{
		// 	URL:    "https://storage.googleapis.com/assets.axieinfinity.com/axies/6073615/axie/axie-full-transparent.png",
		// 	Width:  1280,
		// 	Height: 960,
		// },
	}
	embeds := []*discordgo.MessageEmbed{}
	embeds = append(embeds, embed)
	_, err := session.WebhookExecute(webhook_id, webhook_token, true, &discordgo.WebhookParams{
		// Content: "",
		Embeds: embeds,
	})
	if err != nil {
		fmt.Println("Webhook error:")
		fmt.Println(err)
	}
}
