# What it is
It is a pipleine to to predict the price of nfts going on sale on the Ax1e 1nfinity marketplace. A ML model forescasts the nft price as soon as it is listed and sends a buy notification to Discord if the forecasted price is significantly above the price that it is being listed at. The idea is to flip the nfts in a short time frame, that is, buy them and sell for more in minutes/hours.

# How it works, tech choices, difficulties
image:
<img src="./pipeline_schema.svg" width="1000" alt='schema'>

## Data collection
The ML model is trained with market data. To get the data from the market API, a docker container that runs a Go script is hosted on an ECS cluster. The container is run every 8 hours on a cron job, collecting data in json format for ~10 minutes and then and sending it to an S3 bucket. 

I looked into using AWS lambda for running the cron job but for this usecase this solution turns out to be cheaper. 

Also, I scraped from websites some data that was not directly available from the API. To do so I used selenium directly from my laptop. This Selenium code I copied from another repo and it is not included in this repo or diagram.

## Model training
To train the model, I download the data from S3 to my laptop and run a script that runs a training pipeline locally/on-premise. The pipeline starts by doing some data-validation/tests on the data using a library called Great Expectations, continues with some data cleansing and feature engineering using pandas and numpy and finally trains a few different models on scikit-learn using cross-validation and builds and ensemble model that I store locally.

For the data validation I also looked into other libraries, particularly Pydantic, but choose Great Expectations, which I had already used in a previous project and found simple enough to use for the usecase.

I also trained Tensorflow NeuralNets but found that the model.predict() was not fast enough for serving the model predictions for real time inference (the market is competitive and the buy signals don´t last long). So far I have heard enough praise for Pytorch vs Tensorflow so after this and also after having tried to use Tensorflow Extended unsuccesfully in a previous project, I would like to try Pytorch and possibly ditch Tensorflow for Pytorch if the circustances are right.

## Why I chose Golang

- Because I wanted to learn Go as it is a good language for infrastructure used by many companies. Docker (and Kubernetes) are written in Go. Go Docker containers are lightweight compared with Python Docker containers, which might come in handy for future projects . I also might do robotics in the future and I believe Go is useful for that.

- Because I wanted to do several API calls concurrently to the the market API, to be faster than my competitors and have an edge. I tried Python´s aiohttp library before that but I did not seem provide me with all the capabilities that I was looking for. The fact that some people joke that async code in Python is a nightmare also influenced decision. I did Go, and writing something like a worker pool was fun and easy, as it was learning Go. It is a bit verbose tho.

In order to send concurrent requests to the API without getting flagged I used a proxy service to route my requests through proxies, but found that sending the requests through proxies could add from 10 to 30 seconds delay which was not suitable, so I discarded that and opted to make only a few concurrent requests from my IP. This way additional strain was not inflicted on the API.

## Model serving for Real Time inference and why I use Flask

To be continued

## How long it took me

6 weeks.

# Why I built it

To be continued

