<a id="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![Unlicense License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/auto-code-etri/autocode">
    <img src="assets/dataset_logo.png" alt="Logo" width="100" height="100">
  </a>

  <h3 align="center">A Database Infrastructure in PULSE</h3>

  <p align="center">
     From Ingestion to Management
    <br />
    <a href="https://github.com/auto-code-etri/autocode_dataset/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    &middot;
    <a href="https://github.com/auto-code-etri/autocode_dataset/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
    <br />
    <br />
    PULSE - Pipeline for Unified LLM Software Engineering
    <br />
    <a href="https://github.com/auto-code-etri/autocode"><strong>Explore the PULSE »</strong></a>
    <br />
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

## About The Project
<div align="center">
  <a href="https://github.com/auto-code-etri/autocode_dataset">
    <img src="assets/dataset.png" alt="dataset" width="400" height="400">
  </a>
</div>
<br />

This repository provides a unified collection of code datasets and crawling tools for large-scale software engineering and code intelligence research.

It covers diverse code sources — including coding contests, benchmark datasets, open repositories, and programming communities — enabling a comprehensive approach to data utilization and analysis.

The project integrates data from multiple well-known sources, such as:
  - [![CodeSearchNet][CodeSearchNet]][CodeSearchNet-url]
  - [![GitHub][Github.com]][Github-url]
  - [![StackOverflow][StackOverflow]][StackOverflow-url]
  - [![HumanEval][HumanEval]][HumanEval-url]
  - [![MBPP][MBPP]][MBPP-url]
  - secure code

Together, these datasets and tools establish a comprehensive data infrastructure that supports unified, data-driven research in code understanding, generation, and secure software engineering.

This infrastructure also serves as the data foundation for [![PULSE][pulse-logo]][pulse-url] — a large language model–based framework that automatically generates expert-level, high-quality source code from natural language requirements.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


# Storage (autocode_dataset)

Building a database infrastructure that can be used for additional research of software generation by learning and analyzing codes, documents, and metadata in the source code repository in the future

>- Database storage technology that can be used for program creation/SW analysis

>- Information model technology for generating program source code and improving accuracy of expression

>- Database technology with a structure that facilitates the addition/deletion of source codes within the company

>- Description of code generation evaluation method reflecting actual needs such as code search, summary, and completion

# Overview 
![image](./overview.jpg)

# Requirements of Source Code Infrastructure

>- Multiple source code collection systems provided by multiple organizations must be provided. 
   Currently, Sungkyunkwan University and Suresoft company are in charge of collecting source codes, and the relevant institutions must collect and store data sets according to some guidelines.

>- A system that individually processes the collected source codes must be provided. 
   In addition, source code and natural language should be processed so that they can be easily and immediately used in a third form such as AST or PDG, 
   which can structurally reflect the control and data flow of the program, rather than being stored as they are.

>- It has a data set in which the collected source code and natural language are stored in the form of a database, 
   and a system for using the source code data set that can be extracted from outside using a specific API must be provided.

>- A inter-conversion system between NL and PL must be provided for automatic generation of ML-based source code

>- Automatic generation system of ML-based source code must provide multiple most appropriate source codes

>- When a user makes a query using NL, a function that converts the automatically generated source code to suit the user's environment must be provided.

>- The automatic source code generation system must be provided in the API form so that third parties can easily use it from the outside.

# Crawling Code for Github Project
>- GithubCrawling

This directory contains source code for searching GitHub projects and crawling the source code within those projects. Although the target source codes are in C/C++ and Python, there is no language restriction if the code is modified accordingly.

# Dataset Description
>- CodeSearchNet-Python

This directory contains an augmented dataset based on Python source code from the CodeSearchNet dataset. The original dataset consists of natural language (problem):code pairs, and in this version, the natural language part has been enhanced. In addition to the original problem description, we added solution strategies and pseudocode to enrich the natural language component. This augmented dataset can help improve the ability to find the correct code solutions for given problems.

>- Github-Cpp-2024

This directory contains C/C++ source codes that were crawled, filtered, and collected from GitHub. In particular, during the filtering process, the source codes were scored, and low-quality codes were removed. Additionally, the natural language descriptions for the codes were generated using an LLM, resulting in a complete dataset in the form of (natural language : code) pairs.

>- MutMut

The MutMut dataset was created by applying minor code mutations using a mutation testing tool, with the goal of generating faulty code that fails to pass test cases. These mutations involve various techniques, such as renaming variables, changing operators, and modifying statements—typically at the line level. By applying these transformations to an existing dataset, a collection of buggy code samples was produced.

>- SecureCode-Python

The Secure Code dataset refines the Py150K dataset, ensuring compatibility with Python 3, and applies static analysis to classify the code as secure. Potentially vulnerable snippets are manually reviewed by security experts, following strict guidelines and cross-validation, to preserve their original functionality. The dataset consists of secure code snippets, with deduplication measures in place to prevent data leakage between fine-tuning and evaluation sets.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/auto-code-etri/autocode_dataset.svg?style=for-the-badge
[contributors-url]: https://github.com/auto-code-etri/autocode_dataset/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/auto-code-etri/autocode_dataset.svg?style=for-the-badge
[forks-url]: https://github.com/auto-code-etri/autocode_dataset/network/members
[stars-shield]: https://img.shields.io/github/stars/auto-code-etri/autocode_dataset.svg?style=for-the-badge
[stars-url]: https://github.com/auto-code-etri/autocode_dataset/stargazers
[issues-shield]: https://img.shields.io/github/issues/auto-code-etri/autocode_dataset.svg?style=for-the-badge
[issues-url]: https://github.com/auto-code-etri/autocode_dataset/issues
[license-shield]: https://img.shields.io/badge/LICENSE-ETRI_copyright-blue?style=for-the-badge
[license-url]: https://github.com/auto-code-etri/autocode_dataset/blob/main/LICENSE.txt
[product-image]: assets/dataset.png
[CodeSearchNet]: https://img.shields.io/badge/CodeSearchNet-grey?style=for-the-badge
[CodeSearchNet-url]: https://arxiv.org/abs/1909.09436
[HumanEval]: https://img.shields.io/badge/HumanEval-grey?style=for-the-badge&logo=openai&&logoColor=whithe
[HumanEval-url]: https://arxiv.org/abs/2107.03374
[MBPP]: https://img.shields.io/badge/MBPP-grey?style=for-the-badge&&logo=google&logoColor=blue
[MBPP-url]: https://arxiv.org/abs/1909.09436
[Github.com]: https://img.shields.io/badge/GitHub-%23121011.svg?style=for-the-badge&logo=github&logoColor=white
[Github-url]: https://github.com/
[StackOverflow]: https://img.shields.io/badge/Stack%20Overflow-orange?style=for-the-badge&logo=stackoverflow&logoColor=white
[StackOverflow-url]: https://stackoverflow.com/
[GithubCrawling-url]: https://github.com/auto-code-etri/autocode_dataset/tree/main/GithubCrawling
[pulse-logo]: https://img.shields.io/badge/PULSE-white?style=for-the-badge&logo=data:image/png;base64,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
[pulse-url]: https://github.com/auto-code-etri/autocode
