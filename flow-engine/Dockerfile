# Forge flow-engine image (multi-stage; signed at release time).
FROM golang:1.22 AS build
WORKDIR /src
COPY flow-engine/go.mod ./
RUN go mod download
COPY flow-engine/ ./
RUN CGO_ENABLED=0 go build -o /out/flow-engine ./cmd/flow-engine

FROM gcr.io/distroless/static-debian12
COPY --from=build /out/flow-engine /flow-engine
EXPOSE 8081
ENTRYPOINT ["/flow-engine"]
