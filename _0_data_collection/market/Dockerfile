
##
## Build
##

FROM golang:1.16-buster AS build

WORKDIR /market

COPY go.mod .
COPY go.sum .
RUN go mod download

COPY *.go ./
COPY .env ./

RUN go build -o /collect

##
## Deploy
##

FROM gcr.io/distroless/base-debian10

WORKDIR /

COPY --from=build /collect /collect
COPY --from=build /market/.env .

EXPOSE 8080

USER nonroot:nonroot

CMD ["/collect"]