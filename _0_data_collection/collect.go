package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/credentials"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
)

var URL string = "https://axieinfinity.com/graphql-server-v2/graphql"
var external_api_client = &http.Client{Timeout: time.Second * 10}

const DATE_LAYOUT = "02 Jan 06 15:04 MST"

func main() {
	LoadEnv()
	data := GetData(query_brief_list, 2)
	var sess = ConnectAws()
	SaveData(sess, data, "-suffix")
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
	data := PostRequest(&body, external_api_client)
	var result JsonBlob
	var batch []AxieInfo
	json.Unmarshal([]byte(data), &result)
	batch = ExtractBatchInfo(result)
	return batch
}

func ConnectAws() *session.Session {
	sess, err := session.NewSession(
		&aws.Config{
			Region:      aws.String(AWS_REGION),
			Credentials: credentials.NewStaticCredentials(AWS_KEY_ID, AWS_KEY_PASS, ""),
		})
	if err != nil {
		panic(err)
	}
	return sess
}

func SaveData(sess *session.Session, data []AxieInfo, filename_suffix string) {
	t := time.Now()
	name := fmt.Sprint(t.Format(DATE_LAYOUT)) + filename_suffix
	d, _ := json.Marshal(data)
	uploader := s3manager.NewUploader(sess)
	_, err := uploader.Upload(&s3manager.UploadInput{
		Bucket: aws.String(BUCKET_NAME),
		Key:    aws.String(name),
		Body:   aws.ReadSeekCloser(bytes.NewReader(d)),
	})
	if err != nil {
		panic(err)
	}
}
