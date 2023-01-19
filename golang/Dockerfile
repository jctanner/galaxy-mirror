FROM golang:latest
RUN mkdir -p /app
COPY go.mod /app/go.mod
COPY galaxy_proxy.go /app/galaxy_proxy.go
RUN cd /app; go get github.com/gin-gonic/gin@v1.7.2
RUN cd /app; go get github.com/gin-gonic/gin/binding@v1.7.2
RUN cd /app; go get github.com/gin-gonic/gin/binding@v1.7.2
RUN cd /app; go get github.com/gin-gonic/gin@v1.7.2
RUN cd /app; go get github.com/gin-gonic/gin/binding@v1.7.2
RUN cd /app; go get github.com/gin-gonic/gin/binding@v1.7.2
RUN cd /app; go mod download github.com/gin-gonic/gin
RUN cd /app; go mod download github.com/gin-contrib/location
RUN cd /app; go mod download github.com/gin-gonic/gin

WORKDIR /app
EXPOSE 80
ENTRYPOINT go run galaxy_proxy.go
