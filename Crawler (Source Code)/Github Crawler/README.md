# GitHub Crawler
#### A tool to extract metadata, source code and annotations from GitHub, an open source project repository
<br/>

## Process
1. Get the information of GitHub project in `github_URL_list.csv`
2. Extract metadata(Commits, Watchers, Forks, Stars, Releases, Contributors, Branches, Issues, Pull requests) of GitHub project
3. Get the source code of the GitHub Project in the form of a zip file, unzip file
4. Extract the source code of the desired language (python, c)
5. Extract annotations from the source code


## Requirements
- selenium==4.7.2
- beautifulsoup4==4.11.1


## How to use
1. Write `github_URL_list.csv` in the form (symbol, GitHub URL, source code language) about the GitHub project you want to extract
2. To run `GitHub_Crawler.py`, type a command in the comment window
```
python.\GitHub_Crawler.py
```


## Output Data
- `Codes/[symbol]/[symbol]_[lang]` : Source codes for the desired extension
- `Codes/[symbol]/[symbol]_zip`, `Codes/[symbol]/[symbol]_unzip` : Zip file, Unzip file of source code 
- `Codes/[symbol]_annotation.csv` : Annotations of source code
- `Codes/[symbol]_info.csv` : Metadata of GitHub Project
- `logs.txt` : GitHub Crawler log file