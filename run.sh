#!/bin/bash -x


export PATH="$PATH:/opt/go/bin"

rm -rf /tmp/galaxy-mirror
mkdir -p /tmp/galaxy-mirror
cp *.go /tmp/galaxy-mirror/.
cp *.mod /tmp/galaxy-mirror/.

cd /tmp/galaxy-mirror
#for DEP in $(fgrep github.com go.mod  | fgrep -v module | awk '{print $1}'); do
#    echo "$DEP"
#    go mod download $DEP
#done
go mod download github.com/gin-contrib/location
go mod download github.com/gin-gonic/gin
go get github.com/gin-gonic/gin/binding@v1.7.2
go get github.com/gin-gonic/gin@v1.7.2

export GALAXY_PROXY_CACHE=/vagrant/.cache
go run galaxy_proxy.go
