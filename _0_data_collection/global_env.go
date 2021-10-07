package main

import (
	"log"
	"os"

	"github.com/joho/godotenv"
)

var (
	AWS_REGION   string
	AWS_KEY_ID   string
	AWS_KEY_PASS string
	BUCKET_NAME  string
)

func LoadEnv() {
	err := godotenv.Load()
	if err != nil {
		log.Fatal("Error loading .env file")
	}
	AWS_REGION = os.Getenv("AWS_REGION")
	AWS_KEY_ID = os.Getenv("AWS_KEY_ID")
	AWS_KEY_PASS = os.Getenv("AWS_KEY_PASS")
	BUCKET_NAME = os.Getenv("BUCKET_NAME")

}
