#lotsa imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import codecs
import re
import json
from webdriver_manager.chrome import ChromeDriverManager

def grab_html(site:str):
    """
    gets bs4 soup of site by running a selenium web browser

    args:
        site (str): the site url to fetch
    """
    driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 10)
    driver.get(val)
    get_url = driver.current_url
    wait.until(EC.url_to_be(val))
    if get_url == val:
        page_source = driver.page_source
    soup = BeautifulSoup(page_source,features="html.parser")
    driver.quit()
    return soup

def get_art_info(site:str):
    """
    gets bs4 soup of site by running a selenium web browser

    args:
        site (str): the site url to fetch
    """

def get_trending(soup):
    elements=soup.find(class_="list-widget__content list-unstyled")
    articles=[]
    for elmn in elements:
        art={}
        # Find the element with class "article-card__details" within the current element
        det_elm = elmn.find(class_="article-card__details")
        if det_elm:
            # Find the <a> element within "article-card__details"
            a_element = det_elm.find("a")
            if a_element:
                # Extract the href attribute and the text content
                link = a_element.get("href")
                headline = a_element.find("h3").text
                art["title"]=headline
                infos=get_art_info(link)
                art["publication_date"]=infos["pd"]
                art["author"]=infos["author"]
                art["blurb"]=infos["blurb"]
            articles.append(art)
    return articles

def save_json(infos:list):
    json_data = json.dumps(list_of_dicts)




if __name__=="__main__":
    glink="https://montrealgazette.com/category/news/"
    gaz=grab_html(glink)
    get_trending(gaz)