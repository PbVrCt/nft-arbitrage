package main

import (
	"fmt"

	"github.com/bwmarrin/discordgo"
)

func notify_discord(nft AxieInfoEngineered, webhook_id string, webhook_token string) {
	session, _ := discordgo.New()
	embed := &discordgo.MessageEmbed{
		Title:       "Compra",
		URL:         fmt.Sprint("https://marketplace.axieinfinity.com/axie/", nft.Id),
		Author:      &discordgo.MessageEmbedAuthor{},
		Color:       0x00ff00, // Green
		Description: "Precio:" + fmt.Sprintf("%.0f", nft.Price) + "\nPredicción:" + fmt.Sprintf("%.0f", nft.Prediction),
		Fields: []*discordgo.MessageEmbedField{
			{
				Name:   nft.Class,
				Value:  fmt.Sprint(nft.Mouth, "\n", nft.Back, "\n", nft.Horn, "\n", nft.Tail),
				Inline: true,
			},
			{
				Name:   "Stats",
				Value:  fmt.Sprint("Hp: ", nft.Hp, "\nSpeed: ", nft.Speed, "\nSkill: ", nft.Skill, "\nMorale: ", nft.Morale),
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
	_, err := session.WebhookExecute(webhook_id, webhook_token, true, &discordgo.WebhookParams{
		// Content: "",
		Embeds: embeds,
	})
	if err != nil {
		fmt.Println("Webhook error:")
		fmt.Println(err)
	}
}