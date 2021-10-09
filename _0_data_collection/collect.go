package main

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/feature/s3/manager"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

const URL = "https://axieinfinity.com/graphql-server-v2/graphql"
const DATE_LAYOUT = "2006-01-02T15:04:05Z07:00"

var client = &http.Client{Timeout: time.Second * 10}
var awsS3Client *s3.Client

func main() {
	LoadEnv()
	data := GetData(query_brief_list, 2)
	configS3()
	SaveData(data, ".json")
}

func GetData(query string, pages_to_scan int) []AxieInfo {
	var data []AxieInfo
	for i := 0; i < pages_to_scan; i++ {
		batch := get_data_batch(i, query)
		data = append(data, batch...)
		fmt.Printf("%d", i)
	}
	return data
}

// Gets data from a single post request to the external API
func get_data_batch(page int, query string) []AxieInfo {
	var body RequestBody = CreateBody(page*100, query)
	var batch []AxieInfo
	data, err := PostRequest(&body, client)
	if err != nil {
		return []AxieInfo{}
	}
	var result JsonBlob
	json.Unmarshal([]byte(data), &result)
	batch = ExtractBatchInfo(result)
	return batch
}

func configS3() {
	cfg, err := config.LoadDefaultConfig(context.TODO(), config.WithRegion(AWS_REGION))
	if err != nil {
		log.Fatal(err)
	}
	awsS3Client = s3.NewFromConfig(cfg)
}

func SaveData(data []AxieInfo, filename_suffix string) {
	t := time.Now()
	name := fmt.Sprint(t.Format(DATE_LAYOUT)) + filename_suffix
	d, _ := json.Marshal(data)
	uploader := manager.NewUploader(awsS3Client)
	_, err := uploader.Upload(context.TODO(), &s3.PutObjectInput{
		Bucket: aws.String(BUCKET_NAME),
		Key:    aws.String(name),
		Body:   manager.ReadSeekCloser(bytes.NewReader(d)),
	})
	if err != nil {
		panic(err)
	}
}
