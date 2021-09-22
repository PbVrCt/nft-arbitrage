package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"
)

var URL string = "https://axieinfinity.com/graphql-server-v2/graphql"

func main() {
	b, err := json.Marshal(CreateBody(0))
	if err != nil {
		panic(err)
	}
	request, err := http.NewRequest("POST", URL, bytes.NewBuffer(b))
	if err != nil {
		panic(err)
	}
	request.Header.Set("Content-Type", "application/json")
	client := &http.Client{Timeout: time.Second * 10}
	response, err := client.Do(request)
	if err != nil {
		fmt.Printf("The HTTP request failed with error %s\n", err)
	}
	defer response.Body.Close()
	data, _ := ioutil.ReadAll(response.Body)
	// fmt.Println(string(data))

	var result JsonBlob
	json.Unmarshal([]byte(data), &result)
	info := ExtractInfo(result)
}

// TODO: Send the info through a buffered channel
