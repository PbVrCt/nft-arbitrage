package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

const URL = "https://axieinfinity.com/graphql-server-v2/graphql"
const DATE_LAYOUT = "02 Jan 06 15:04 MST"

var awsS3Client *s3.Client
var data_bucket []AxieInfo

func main() {
	LoadEnv()
	configS3()
	data_bucket = DownloadS3Bucket()
	file, _ := json.MarshalIndent(data_bucket, "", " ")
	_ = ioutil.WriteFile("../data/full_raw.json", file, 0644)
}

func configS3() {
	cfg, err := config.LoadDefaultConfig(context.TODO(), config.WithRegion(AWS_REGION))
	if err != nil {
		log.Fatal(err)
	}
	awsS3Client = s3.NewFromConfig(cfg)
}

func DownloadS3Bucket() []AxieInfo {
	var prefix string
	var delimeter string
	paginator := s3.NewListObjectsV2Paginator(awsS3Client, &s3.ListObjectsV2Input{
		Bucket:    aws.String(BUCKET_NAME),
		Prefix:    aws.String(prefix),
		Delimiter: aws.String(delimeter),
	})
	for paginator.HasMorePages() {
		page, _ := paginator.NextPage(context.TODO())
		for _, item := range page.Contents {
			object, _ := awsS3Client.GetObject(context.TODO(), &s3.GetObjectInput{
				Bucket: aws.String(BUCKET_NAME),
				Key:    aws.String(*item.Key),
			})
			data, _ := ioutil.ReadAll(object.Body)
			var batch []AxieInfo
			json.Unmarshal([]byte(data), &batch)
			data_bucket = append(data_bucket, batch...)
			fmt.Print(batch[0].Class, "\n")
		}
	}
	return data_bucket
}

type AxieInfo struct {
	Date       string
	Id         int
	Class      string
	PriceBy100 float64
	PriceUSD   float64
	BreedCount int
	Genes      string
	Eyes       string
	Ears       string
	Back       string
	Mouth      string
	Horn       string
	Tail       string
	EyesType   string
	EarsType   string
	BackType   string
	MouthType  string
	HornType   string
	TailType   string
}
