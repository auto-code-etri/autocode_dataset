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
    <img src="assets/fulse.png" alt="Logo" width="80" height="80">
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
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
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
[![Product Image][product-image]](https://github.com/auto-code-etri/autocode_dataset)


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
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-image]: images/dataset.png
[Next.js]: https://img.shields.io/badge/next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white
[Next-url]: https://nextjs.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Vue.js]: https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vuedotjs&logoColor=4FC08D
[Vue-url]: https://vuejs.org/
[Angular.io]: https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white
[Angular-url]: https://angular.io/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Laravel.com]: https://img.shields.io/badge/Laravel-FF2D20?style=for-the-badge&logo=laravel&logoColor=white
[Laravel-url]: https://laravel.com
[Bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[Bootstrap-url]: https://getbootstrap.com
[JQuery.com]: https://img.shields.io/badge/jQuery-0769AD?style=for-the-badge&logo=jquery&logoColor=white
[JQuery-url]: https://jquery.com 
