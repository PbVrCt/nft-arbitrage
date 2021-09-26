package main

import (
	"log"
	"os"

	"github.com/joho/godotenv"
)

var (
	PRX           string
	DISCORD_ID    string
	DISCORD_TOKEN string
)

func InitConfig() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}
	PRX = os.Getenv("URL2")
	DISCORD_ID = os.Getenv("DISCORD_WEBHOOK_ID")
	DISCORD_TOKEN = os.Getenv("DISCORD_WEBHOOK_TOKEN")

}
