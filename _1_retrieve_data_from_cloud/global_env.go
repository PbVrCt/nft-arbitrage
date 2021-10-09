package main

import (
	"log"
	"os"

	"github.com/joho/godotenv"
)

var (
	AWS_REGION            string
	AWS_ACCESS_KEY_ID     string
	AWS_SECRET_ACCESS_KEY string
	BUCKET_NAME           string
)

func LoadEnv() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}
	AWS_REGION = os.Getenv("AWS_REGION")
	AWS_ACCESS_KEY_ID = os.Getenv("AWS_ACCESS_KEY_ID")
	AWS_SECRET_ACCESS_KEY = os.Getenv("AWS_SECRET_ACCESS_KEY")
	BUCKET_NAME = os.Getenv("BUCKET_NAME")

}
