'''
GitHub Crawler
Created on Thu Jan 5 2023

@author: Heewon Baek
'''


import zipfile
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import os, shutil
import urllib.request as urllib2
from time import ctime, sleep
from colorama import Fore
import re
import csv


def LOGD(string, attr = (), depths = 0, color = 0):  ## logs.txt 파일에 로그 작성
    if color == 0:
        print(Fore.WHITE + ' ' * depths + '[%s] ' % (ctime()) + string % (attr))
    elif color == 1:
        print(Fore.RED + ' ' * depths + '[%s] ' % (ctime()) + string % (attr))
    fp = open("logs.txt", "a")
    fp.write(' ' * depths + '[%s] ' % (ctime()) + string % (attr) + '\n')
    fp.close()


annoation_dict = {"py": ["#.*\n*","\'\'\'[\S\s]*?\'\'\'\n*","\"\"\"[\S\s]*?\"\"\"\n*"], "c": ["\/\*[\S\s]*?\*\/\n*", "\/\/.*\n*"]}
annoation_except = ["\/\/[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&\'\(\)\*\+,;=.]+$", "\/\/.+[^/\s/g]"]


class GitHubCrawler:
    def __init__(self):
        fp = open("logs.txt", 'w')
        fp.close()
        self.driver_wait_time = 5
        self.sleep_time = 1
        self.download_folder = "Codes"
        if not os.path.exists(self.download_folder):
            os.mkdir(self.download_folder)
        self.urlList = {}
        self.driver = webdriver.Firefox(executable_path='modules\\geckodriver.exe')


    def Destroy(self):  ## webdriver 구동 해제
        self.driver.quit()


    def FindAll(self, code):  ## 현재 페이지의 파라미터 값이 의미하는 태그를 모두 리턴
        html = self.driver.page_source
        soup = bs(html, 'html.parser')
        return soup.find_all(code)


    def OpenURL(self, url):  ## 해당 url로 이동
        while True:
            self.driver.get(url)  
            self.driver.implicitly_wait(self.driver_wait_time)
            sleep(self.sleep_time)
            check_whoa = self.FindAll('div')  
            check_whoa_tf = False 
            for code in check_whoa:
                code = code.decode()
                if 'Whoa there!' in code:
                    check_whoa_tf = True
            if not check_whoa_tf:  
                break
            sleep(15)


    def ReadCSV(self, filename):  ## csv파일을 읽어서 urlList 생성
        fp = open(filename, 'r', encoding='utf-8', errors='ignore') 
        lines = fp.readlines()  
        fp.close()
        for line in lines: 
            line = line.replace('\n','').split(',')  
            if line[1] == '':  
                continue
            self.urlList[line[0]] = {'URL': line[1], 'Lang': line[2]}


    def Download(self):  ## log에 해당 github url의 metadata 정보 출력 및 [symbol]_info.csv에 정보 저장
        LOGD("Start Maintain Parser.", (), 1)
        for symbol in self.urlList:
            LOGD("Target Github: %s (%d/%d)", (symbol, list(self.urlList.keys()).index(symbol) + 1, len(list(self.urlList.keys()))), 2)
            LOGD("Open URL: %s", (self.urlList[symbol]['URL']), 3)  
            self.OpenURL(self.urlList[symbol]['URL'])  
            CommitNum, Branches, Releases, Contributors, Watch, Star, Fork, Issues, Pull = self.GetCommitNum(self.urlList[symbol]['URL'])
            if CommitNum == -1:
                LOGD("Page disappeared. Symbol: %s", (symbol), 10, 1)
                continue  
            LOGD("Commit num: %d", (CommitNum), 3)
            LOGD("Branches: %d, Releases: %d, Contributors: %d", (Branches, Releases, Contributors), 4)
            LOGD("Watch: %d, Star: %d, Fork: %d, Issues: %d, Pull: %d", (Watch, Star, Fork, Issues, Pull), 4)
            
            if not os.path.exists('./' + self.download_folder + '/'+symbol): 
                os.mkdir('./' + self.download_folder + '/'+symbol)
            fp = open('./' + self.download_folder + '/' + symbol + '/' + symbol + '_info.csv', 'w')
            fp.write('Commits, Branches, Releases, Contributors, Watch, Star, Fork, Issues, Pull\n')
            fp.write('%d, %d, %d, %d, %d, %d, %d, %d, %d' % (CommitNum, Branches, Releases, Contributors, Watch, Star, Fork, Issues, Pull))
            fp.close()
            self.DownloadProcess((self.urlList[symbol]['URL']), symbol)


    def GetCommitNum(self, url):  ## 해당 github url의 metadata 추출
        dictionary = {}
        # Watchers, Forks, Stars, Releases, Contributors, Branches
        codes = self.FindAll('div')
        for code in codes:
            code = code.decode()
            if 'BorderGrid-row hide-sm hide-md' in code:
                code = code.split('</div>')
                for index in range(0, len(code)):
                    if 'Watchers' in code[index] or 'Forks' in code[index] or 'Stars' in code[index]:
                        tmp = code[index].split('</strong>')[0].split('>')[-1]
                        dictionary[code[index].split('</h3>')[0].split('>')[-1]] = tmp  
            if 'h4 mb-3' in code:
                code = code.split('</span>')
                for index in range(0, len(code)):
                    if 'Releases' in code[index]:
                        if code[index].split('\n')[-2].replace(' ','') == 'Releases':
                            tmp = code[index].split('\n')[-1].split('>')[-1]  
                            dictionary[code[index].split('\n')[-2].replace(' ','')] = tmp 
                    if 'Contributors' in code[index]:
                        if code[index].split('<span')[0].split('\n')[-1].replace(' ','') == 'Contributors':
                            tmp = code[index].split('>')[-1] 
                            dictionary[code[index].split('<span')[0].split('\n')[-1].replace(' ','')] = tmp  
            if 'flex-self-center ml-3 flex-self-stretch d-none d-lg-flex flex-items-center lh-condensed-ultra' in code:
                code = code.split('</span>')
                for index in range(0, len(code)):
                    if 'branches' in code[index]:
                        if code[index].split('>')[-1] == 'branches':
                            tmp = code[index].split('</strong>')[0].split('<strong>')[-1]  
                            dictionary['Branches'] = tmp 
        # Commits
        codes = self.FindAll('li')
        for code in codes:
            code = code.decode()
            if 'ml-0 ml-md-3' in code:
                tmp = code.split('</strong>')[0].split('<strong>')[1] 
                dictionary['Commits'] = tmp
        # Issues, Pull requests
        codes = self.FindAll('nav')
        for code in codes:
            code = code.decode()
            if '"Repository"' in code:
                code = code.split('</svg>')
                for index in range(2, (4 if 4 < len(code) else len(code))):
                    if 'Issues' in code[index] or 'Pull requests' in code[index]:
                        tmp = code[index].split('</span>')[1].split('">')[-1].replace(',','')
                        dictionary[code[index].split('</span>')[0].split('">')[-1]] = tmp

        commits = -1
        branches = 0
        releases = 0
        contributors = 0
        watch = 0
        star = 0
        fork = 0
        issues = 0
        pull = 0
        
        if 'Commits' in dictionary.keys():
            commits = int(dictionary['Commits'].replace(',',''))
        elif 'Commits' in dictionary.keys():
            commits = int(dictionary['Commits'].replace(',',''))
        if 'Branches' in dictionary.keys():
            branches = int(dictionary['Branches'].replace(',',''))
        elif 'Branches' in dictionary.keys():
            branches = int(dictionary['Branches'].replace(',',''))
        if 'Releases' in dictionary.keys():
            releases = int(dictionary['Releases'].replace(',',''))
        elif 'Release' in dictionary.keys():
            releases = int(dictionary['Releases'].replace(',',''))
        if 'Contributors' in dictionary.keys():
            if '+' in dictionary['Contributors'] or ',' in dictionary['Contributors']:
                contributors = int(dictionary['Contributors'].replace('+','').replace(',',''))
            else:
                contributors = int(dictionary['Contributors'])
        if 'Watchers' in dictionary.keys():
            if 'k' in dictionary['Watchers']:
                watch = int(float(dictionary['Watchers'].split('k')[0]) * 1000)
            else:
                watch = int(dictionary['Watchers'])
        if 'Stars' in dictionary.keys():
            if 'k' in dictionary['Stars']:
                star = int(float(dictionary['Stars'].split('k')[0]) * 1000)
            else:
                star = int(dictionary['Stars'])
        if 'Forks' in dictionary.keys():
            if 'k' in dictionary['Forks']:
                fork = int(float(dictionary['Forks'].split('k')[0]) * 1000)
            else:
                fork = int(dictionary['Forks'])
        if 'Issues' in dictionary.keys():
            if 'k' in dictionary['Issues'] or 'k+' in dictionary['Issues']:
                issues = int(float(dictionary['Issues'].split('k')[0]) * 1000)
            else:
                issues = int(dictionary['Issues'])
        if 'Pull requests' in dictionary.keys():
            pull = int(dictionary['Pull requests'])
            
        return commits, branches, releases, contributors, watch, star, fork, issues, pull


    def DownloadProcess(self, url, symbol):  ## Download 과정
        self.OpenURL(url)
        LOGD("Get the download zip addr.", (), 3)
        zip_addr = self.FindDownloadZipButton()
        if zip_addr == -1:
            LOGD("Finding the download button failed...", (), 10, 1)
        LOGD("Start to download the zip.", (), 3)
        downPath = self.DownZip(zip_addr, symbol)
        if downPath == -1:
            LOGD("Downloading is failed...", (), 10, 1)
        else:
            LOGD("Zip downloading success.", (), 3)


    def FindDownloadZipButton(self):  ## Download ZIP 버튼 찾아서 다운로드 URL 리턴
        codes = self.FindAll('a')
        for code in codes:
            code = code.decode()
            if 'DOWNLOAD_ZIP' in code:
                return 'https://github.com' + code.split('href="')[1].split('"')[0]
        return -1


    def DownZip(self, zip_addr, symbol):  ## zip 파일 다운로드
        downPath = self.download_folder + '/' + symbol + '/' + symbol + '.zip'
        countTries = 0
        while True:
            if countTries >= 5:
                LOGD("zipAddr: %s", zip_addr)
                return -1
            try:
                req = urllib2.Request(zip_addr)
                f = urllib2.urlopen(req)
                if f.getcode() == 200:
                    break
            except Exception as e:
                LOGD("Zip downloading error. # of trial = %d", countTries, 10, 1)
                LOGD("Error: %s", e, 10, 1)
                countTries = countTries + 1
        zipFile = open(downPath, 'wb')
        zipFile.write(f.read())
        zipFile.close()
        f.close()
        return downPath


    def UnZip(self):  ## zip 파일 압축 해제
        LOGD("Start to unzip.", (), 2)
        for symbol in self.urlList.keys():
            try:
                zipPath = 'Codes/' + symbol + '/' + symbol +'.zip'
                unZipPath = 'Codes/' + symbol + '/' + symbol + '_unzip'
                if not os.path.exists(unZipPath):
                    os.mkdir(unZipPath)
                unzip = zipfile.ZipFile(zipPath)
                unzip.extractall(unZipPath)
                unzip.close()
            except Exception as e:
                LOGD("Unzip error... %s", zipPath, 10, 1)
                return -1
        LOGD("Unzip complete.", (), 2)
        return 0


    def Extract_Code_and_Annotation(self):  ## 원하는 파일 및 주석 추출
        for symbol in self.urlList.keys():
            lang = self.urlList[symbol]['Lang']
            self.Extract_Code(symbol, lang)
            self.Extract_Annotation(symbol, lang)
        
            
    def Extract_Code(self, symbol, lang):  ## 원하는 파일 추출
        LOGD("Start to extract files.", (), 2)
        fileList = []
        targetPath = 'Codes/' + symbol + '/' + symbol + '_unzip/'
        for (path, dir, files) in os.walk(targetPath):
            for filename in files:
                ext = os.path.splitext(filename)[-1]
                if ext == '.' + lang:
                    fileList.append(path + '/' + filename)
        if not fileList:
            LOGD("No %s file in %s.", (lang, targetPath), 3)
        else:
            extPath = 'Codes/' + symbol + '/' + symbol + '_' + lang
            if not os.path.exists(extPath):
                os.mkdir(extPath)
            for source in fileList:
                shutil.copy(source, extPath)
        LOGD("Extracting files complete.", (), 2)
    
    
    def Extract_Annotation(self, symbol, lang): ## 주석 추출
        LOGD("Start to extract annotation.", (), 2)
        targetPath = 'Codes/' + symbol + '/' + symbol + '_' + lang
        for filename in os.listdir(targetPath):
            annot = ""
            with open(os.path.join(targetPath, filename), 'r', encoding='UTF-8') as f:
                file = f.read()
                if lang == 'c':
                    annot = self.Extract_C_Annotation(lang, file)
                else:
                    annot = self.Extract_PY_Annotation(lang, file)
                f.close()
                fp = open('Codes/' + symbol + '/' + symbol + '_annotation.csv', 'a', encoding='UTF-8')
                wr = csv.writer(fp)
                wr.writerow([filename, annot])
                fp.close()
        LOGD("Extracting annotations complete.", (), 2)
    
    
    def Extract_C_Annotation(self, lang, file): ## C 주석 추출
        annot = ""
        for regex in annoation_dict[lang]:
            if regex == '\/\/.*\n*': # 주석이 //인 경우
                tmp = re.compile(regex).findall(file)
                for sentence in tmp:
                    # URL regex 및 //뒤에 아무것도 없는 주석 제거
                    if (re.compile(annoation_except[0]).match(sentence) == None) and (re.compile(annoation_except[1]).match(sentence) != None):
                        annot += sentence
            else:
                annot += '\n'.join(re.compile(regex).findall(file))
        return annot
             
                
    def Extract_PY_Annotation(self, lang, file): ## python 주석 추출
        annot = ""
        for regex in annoation_dict[lang]:
            annot += '\n'.join(re.compile(regex).findall(file))
        return annot
                        
                
                
if __name__ == '__main__':  #python .\GitHub_Crawler.py
    LOGD("Program Starting! Name: %s", (os.path.basename(__file__)))
    handler = GitHubCrawler()
    handler.ReadCSV('github_URL_list.csv')
    handler.Download()
    handler.UnZip()
    handler.Extract_Code_and_Annotation()
    handler.Destroy()
    LOGD("Program End!", (), 1)