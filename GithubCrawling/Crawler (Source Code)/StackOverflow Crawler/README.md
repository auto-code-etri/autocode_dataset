<a id="readme-top"></a>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project---stackoverflow-crawler">About the Project - StackOverflow Crawler</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#working-process">Working Process</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
      <ul>
        <li><a href="#output-data">Output Data</a></li>
      </ul>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>
<br/>

## About the Project - StackOverflow Crawler
A tool to extract source code and annotations from StackOverflow.

### Built With
This project was built using the following main libraries and frameworks:
- [![Python][Python.org]][Python-url]
- [![Selenium][Selenium.dev]][Selenium-url]
- [![BeautifulSoup][BeautifulSoup-logo]][BeautifulSoup-url]
- [![Colorama][Colorama-logo]][Colorama-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started
### Prerequisites
- `selenium==4.7.2`
- `beautifulsoup4==4.11.1`
- Download the version of [chromedriver](https://chromedriver.chromium.org/downloads) that fits your computer and replace `chromedriver.exe`

### Working Process

1. Get the information of StackOverflow search keyword in `sample.csv`
2. Get the answer url of top N page you set by args
3. Extract the source code of the desired language in side the url

## Usage
1. Write search keyword inside `sample.csv`
2. To run `stackoverflow_downloader.py` with options
```
python.\stackoverflow_downloader.py
```

### Output Data
- `Codes/code.csv` : Source codes for the desired extension


<p align="right">(<a href="#readme-top">back to top</a>)</p>



## Contributors:

<a href="https://github.com/auto-code-etri/autocode_dataset/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=auto-code-etri/autocode_dataset" alt="contrib.rocks image" />
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Copyright *On-Device AI Model Research Laboratory, ETRI*.

All rights reserved. For more details, see `LICENSE.txt`.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgment
> This work was supported by Institute of Information & communications Technology Planning & Evaluation (IITP) grant funded by the Korea government(MSIT) (No.2022-0-00995, Automated reliable source code generation from natural language descriptions)

> 이 논문은 2025년도 정부(과학기술정보통신부)의 재원으로 정보통신기획평가원의 지원을 받아 수행된 연구임 (No.2022-0-00995, 자연어로 기술된 요구사항에서 전문 개발자 수준의 고품질 코드를 자동 생성하는 기술 개발)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[Python.org]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Selenium.dev]: https://img.shields.io/badge/Selenium-red?style=for-the-badge&logo=selenium&logoColor=white
[Selenium-url]: https://www.selenium.dev/
[BeautifulSoup-logo]: https://img.shields.io/badge/BeautifulSoup-4B8BBE?style=for-the-badge&logo=python&logoColor=white
[BeautifulSoup-url]: https://www.crummy.com/software/BeautifulSoup/
[Colorama-logo]: https://img.shields.io/badge/Colorama-FECA57?style=for-the-badge&logo=python&logoColor=black
[Colorama-url]: https://pypi.org/project/colorama/