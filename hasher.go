package main

import (
	"fmt"
    "hash/fnv"
	"os"
)

func hash(s string) string {
    h := fnv.New32a()
    h.Write([]byte(s))
    return fmt.Sprint(h.Sum32())
}



func main() {
    url := os.Args[1]
    hashed := hash(url)
    fmt.Println(hashed)
}
