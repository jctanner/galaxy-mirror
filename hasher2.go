package main

import (
    "crypto/sha256"
    //"encoding/base64"
    "encoding/hex"
    "fmt"
    "os"
)

func hash(s string) string{
    hasher := sha256.New()
    hasher.Write([]byte(s))
    //sha := base64.URLEncoding.EncodeToString(hasher.Sum(nil))
    sha := hex.EncodeToString(hasher.Sum(nil))
	return string(sha)
}

func main() {
	url := os.Args[1]
    hashed := hash(url)
    fmt.Println(hashed)
}
