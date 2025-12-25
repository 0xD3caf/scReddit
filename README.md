# Welcome to ScrapeReddit (scReddit) V1.0
Developed and Tested on Ubuntu 24.04.3 LTS using Chrome Version 143.0.7499.169 and Python3.12

No testing has been done on Windows or Mac but it should work as long as you have Python3.

This tool allows easy downloading of gifs from Reddit. Currently supported gif / video providers are
- i.redd.it
- redgifs
- giphy

## Requirements
This tool requires Python3 and redgifs downloader. The redgifs downloader is available through pip
```bash
pip install redgifs
```

## Basic Usage
```
Python3 scReddit.py [options] -s <subreddit> -r
```
Or Make the file executable and run it directly
```
chmod +x scReddit.py
./scReddit.py [options] -s <subreddit> -r
```

### FLAGS
```
-s (--sub)   -> Target sub to scrape, only include the subreddit name
-r (--run)   -> Activates full operation, in this mode files WILL be downloaded
-t (--top)   -> Downloads top all time posts instead of most recent
-c (--count) -> Sets the number of pages to be downloaded, Defaults to 10.
-x (--xpost) -> Follows crossposts and adds them to downloads queue
-p (--path)  -> Sets the location to store downloaded files. Defaults to "downloads"
-d (--debug) -> Prints debug messages to the console during operation
```


## Examples
```
# This will download the top all time Gifs from /r/gifs
./scReddit.py -r -t -s gifs

# This downloads the top 5 pages of hottest posts
./scReddit.py -r -c 5 -s gifs
```
