package main

import (
	"fmt"
	"time"

	"github.com/bwmarrin/discordgo"
)

func main() {
	fmt.Println("Hello go")
	session, _ := discordgo.New()
	embeds := []*discordgo.MessageEmbed{}
	embed := &discordgo.MessageEmbed{
		Title:       "Planta",
		URL:         "https://marketplace.axieinfinity.com/axie/6073615",
		Author:      &discordgo.MessageEmbedAuthor{},
		Color:       0x00ff00, // Green
		Description: "Precio: 100\nPredicción: 300 ",
		Fields: []*discordgo.MessageEmbedField{
			&discordgo.MessageEmbedField{
				Name:   "Cartas",
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
		Timestamp: time.Now().Format(time.RFC3339), // Discord wants ISO8601; RFC3339 is an extension of ISO8601 and should be completely compatible.
	}
	embeds = append(embeds, embed)
	_, err := session.WebhookExecute("884600286398804009", "AekOhZuGMldcimEzafjgweN2hq-i1ET2G9uwdYjb3vpxREK6Rw8yrZyon_z8UFeJnQXL", true, &discordgo.WebhookParams{
		// Content: "",
		Embeds: embeds,
	})
	if err != nil {
		fmt.Println("Webhook error:")
		fmt.Println(err)
	}
}
