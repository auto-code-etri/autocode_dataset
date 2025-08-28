import re
from selenium import webdriver
from bs4 import BeautifulSoup as bs
import os
from time import ctime, sleep
from colorama import Fore
from selenium.webdriver.common.by import By
import csv
from pathlib import Path
import argparse
import re

def LOGD(string, attr = (), depths = 0, color = 0):  ####logs.txt 파일에 로그 작성 함수
    if color == 0:
        print(Fore.WHITE + ' ' * depths + '[%s] ' % (ctime()) + string % (attr))
    elif color == 1:
        print(Fore.RED + ' ' * depths + '[%s] ' % (ctime()) + string % (attr))
    fp = open("logs.txt", "a")
    fp.write(' ' * depths + '[%s] ' % (ctime()) + string % (attr) + '\n')
    fp.close()

    
def is_valid_href(href):
    if re.match('^\/question+', href):
        return True
    else :
        return False

def parse_language(str : str):
    """
        find language in string
    """
    str = str.strip()
    if str == "*":
        return "all"
    return str.split(",")
    

annotation_dict = {"cpp" : ["\/{2}.*\n*","\/\*([\S\s])*\*\/"], "c" : ["\/{2}.*\n*","\/\*[\S\s]*?\*\/"], "java" : ["\/{2}.*\n*","\/\*([\S\s])*\*\/"], 
"python" : ["#.*\n*","\"\"\"([\S\s])*?\"\"\"","'''([\S\s])*?'''"]}


""""ㅁㄴㅇㅁ"""""
class Downloader:
    def __init__(self, driver_wait_time, sleep_time, input_csv_path = "./sample.csv", output_csv_path="./Codes/code.csv", upvote_limit = 0, search_page_limit = 4, language = "cpp,java"):
        fp = open("logs.txt", 'w')
        fp.close()

        # Driver config
        self.driver_wait_time = driver_wait_time
        self.sleep_time = sleep_time

        # Download restriction
        self.upvote_limit = upvote_limit
        self.search_page_limit = search_page_limit
        self.language_to_search = parse_language(language)

        # Folder config
        self.input_csv_path = input_csv_path
        self.output_folder, self.output_csv = os.path.split(output_csv_path)
        self.output_csv_path = output_csv_path


        if not Path(input_csv_path).is_file():
            print("input file doesn't exist")
            exit(1)

        if not Path(self.output_folder).exists():
            os.makedirs(self.output_folder)

        @property
        def input_csv_path(self):
            return self.input_csv_path

        @input_csv_path.setter
        def input_csv_path(self, value):
            if not Path(value).is_file():
                print("input file doesn't exist")
                exit(1)
            self.input_csv_path = value

        @property
        def output_csv(self):
            return self.output_csv

        @output_csv.setter
        def output_csv(self, value):
            self.output_csv = value

        @property
        def output_csv_path(self):
            return self.output_csv_path

        @output_csv_path.setter
        def output_csv_path(self, value):
            self.output_folder, self.output_csv = os.path.split(value)
            if not Path(self.output_folder).exists():
                os.makedirs(value)
            self.output_csv_path = value

        fp = open(self.output_csv_path,'w+')
        writer = csv.writer(fp)
        writer.writerow(["language","code","annotation"])
        fp.close()
    
        self.search_list = []
        options = webdriver.ChromeOptions()
        
        self.driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver',options=options)

    
    def Destroy(self):  
        self.driver.quit()

    def find_all_elements(self, tag, class_name):  
        """
            현재 페이지의 파라미터 값이 의미하는 태그를 모두 리턴
            tag: 검색 하려는 string의 태그
        """

        html = self.driver.page_source 
        soup = bs(html, 'html.parser') 
        return soup.find_all(tag, class_name,href=True) 
      
    def is_upvote_above_limit(self,code):
        upvote = int(code.find_element(By.CSS_SELECTOR,".js-vote-count").text)
    
        if upvote == None:
            LOGD("no upvote")
            return False
        if upvote >= self.upvote_limit:
            return True
        else:
            return False

    def get_code_from_answer_html(self, HTML_obj):
        if len(HTML_obj.find_elements(By.CSS_SELECTOR,".hljs")):
            return HTML_obj.find_element(By.CSS_SELECTOR,".hljs").get_attribute("innerText")

    def get_answer_htmls(self,answer):
        """
            Retun List of selenium Object if the DOM includes language inside language_to_search dict
        """
        #TODO by using ARGPARSE you have to change by finding language that has been added by cmd arguments
        for language in self.language_to_search:
            try :
                answer.find_element(By.CSS_SELECTOR,f".language-{language}")
                return f"{language}", answer.find_elements(By.CSS_SELECTOR,".js-answer")
            except:
                LOGD(f"{language} not found")
            
        return False,False

    def parse_code_and_annotation(self,url):
        """
            parse code block in url
            (str) url : url to stackoverflow question
        """
        self.driver.get(url)
        self.driver.implicitly_wait(self.driver_wait_time)

        # return selenium object after answers ID
        answer_elements = self.driver.find_element(By.ID, "answers")

        code_lang, answer_list = self.get_answer_htmls(answer_elements)
        if code_lang:
            for answer in answer_list:
                if self.is_upvote_above_limit(answer):
                    print(f"{code_lang} over vote")
                    code = self.get_code_from_answer_html(answer)
                    if code:
                        annot = ""
                        code_without_annot = code
                        for regex in annotation_dict[code_lang]:
                            code_without_annot = re.compile(regex).sub('',code_without_annot)
                            annot += '\n'.join(re.compile(regex).findall(code))
                        self.add_code_and_annot_to_csv([code_lang,code_without_annot,annot])
                else:
                    print(f"{code_lang} under vote")

    def find_answer_url_from_sel_page(self):
        """
            search for stack overflow answer link in page and return links as list
        """
        href_list = []
        while True:
            LOGD("find_answer_url")
        
            self.driver.implicitly_wait(self.driver_wait_time)
            sleep(self.sleep_time)
            answer_links = self.find_all_elements('a','s-link')
            for answer_link in answer_links:
                href = answer_link.attrs['href']
                if is_valid_href(href):
                    href_list.append(href)
            if href:
                break
            
        return href_list
    
    def get_code_from_search_list_add_to_csv(self):
        """
            get code from top N answer in stackoverflow
        """
        for search_keyword in self.search_list:
            href_list = []
            # find code url in page and add to href list
            
            for i in range(1,self.search_page_limit):
                print('https://stackoverflow.com/search?page={}&q={}'.format(i,search_keyword))
                self.driver.get('https://stackoverflow.com/search?page={}&q={}'.format(i,search_keyword))
                href_list.extend(self.find_answer_url_from_sel_page())
            # find code inside question page
            for href in href_list:
                URL = "https://stackoverflow.com{}".format(href)
                self.parse_code_and_annotation(URL)
                
    def create_search_list_from_csv(self):  
        fp = open(self.input_csv_path, 'r', encoding='utf-8', errors='ignore')  
        lines = fp.readlines() 
        fp.close()
        for line in lines: 
            line = line.replace('\n','').split(',')
            if line[0] == '': 
                continue
            self.search_list.append(line[0])

    def add_code_and_annot_to_csv(self, code):
        fp = open(self.output_csv_path,'a+')
        writer = csv.writer(fp)
        writer.writerow(code)
        fp.close()
    
    def download(self):
        self.create_search_list_from_csv()
        self.get_code_from_search_list_add_to_csv()


parser = argparse.ArgumentParser(
                    prog = 'crawler',
                    description = 'What the program does',
                    epilog = 'Text at the bottom of help')

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('-l','--language', type=str, 
                    help='crawler language type', default="c,python")
parser.add_argument('-w','--wait_time', type=int, default= 10,
                    help='selenium driver wait time')
parser.add_argument('-ul','--upvote_limit', type=int, default= 0,
                    help='Vote number threshold')
parser.add_argument('-spl','--search_page_limit', type=int, default= 2,
                    help='Page numbers to search')
parser.add_argument('-icp','--input_csv_path', type=str, default= "./sample.csv",
                    help='path to keywords')
parser.add_argument('-ocp','--output_csv_path', type=str, default= "./Codes/code.csv",
                    help='path to create code.csv')                            
args = parser.parse_args()
# if __name__ == '__main__': 
    
LOGD("Program Starting! Name: %s", (os.path.basename(__file__)))  
handler = Downloader(input_csv_path=args.input_csv_path, output_csv_path=args.output_csv_path, search_page_limit=args.search_page_limit, upvote_limit=args.upvote_limit, language=args.language,sleep_time=args.wait_time,driver_wait_time=args.wait_time)
handler.download()
LOGD("Program End!", (), 1)