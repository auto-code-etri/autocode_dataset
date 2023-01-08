# Stackoverflow Crawler

#### A tool to extract source code and annotations from Stackoverflow

<br/>

## Process

1. Get the information of Stackoverflow search keyword in `sample.csv`
2. Get the answer url of top N page you set by args
3. Extract the source code of the desired language in side the url

## Requirements

- selenium==4.7.2
- beautifulsoup4==4.11.1
- Download the version of [chromedriver](https://chromedriver.chromium.org/downloads) that fits your computer and replace `chromedriver.exe`

## How to use

1. Write search keyword inside `sample.csv`
2. To run `stackoverflow_downloader.py` with options

```
python.\stackoverflow_downloader.py
```

## Output Data

- `Codes/code.csv` : Source codes for the desired extension
