#lotsa imports
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import codecs
import re
import json
import requests
# from webdriver_manager.chrome import ChromeDriverManager
import logging

logger=logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)

# def grab_html_selenium(site:str):
#     """
#     gets bs4 soup of site by running a selenium web browser

#     args:
#         site (str): the site url to fetch
#     """
#     driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()))
#     wait = WebDriverWait(driver, 10)
#     driver.get(site)
#     get_url = driver.current_url
#     wait.until(EC.url_to_be(site))
#     # logger.debug("Fetching news from {}".format(site))
#     if get_url == site:
#         page_source = driver.page_source
#     soup = BeautifulSoup(page_source,features="html.parser")
#     driver.quit()
#     return soup

def grab_html(site:str):
    """
    gets bs4 soup of site by using requests

    args:
        site (str): the site url to fetch
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    result = requests.get(site, headers=headers)
    # return result.content.decode()
    soup = BeautifulSoup(result.content.decode(),features="html.parser")
    return soup
    # print(result.content.decode())

def get_art_info(site:str):
    """
    gets montreal gazette article page info using bs4 soup dump

    args:
        site (str): the site url to get the info of
    """
    NEWS_QUERY_STRING_TEMPLATE="https://montrealgazette.com{}"
    query_string=NEWS_QUERY_STRING_TEMPLATE.format(site)

    soup=grab_html(query_string)
    
    # Get the text of p element with class "article-subtitle"
    article_subtitle = soup.find('p', class_='article-subtitle').text

    # Get the text of span element with class "published-by__author"
    author = soup.find('span', class_='published-by__author')
    if (not author):
        author = soup.find('div', class_='wire-published-by__company')
    author=author.text

    # Get the text of span element with class "published-date__since"
    published_date = soup.find('span', class_='published-date__since').text

    # Print the results
    print("Article Subtitle:", article_subtitle)
    print("Author:", author)
    print("Published Date:", published_date)
    return {"pd": published_date, "author": author, "blurb": article_subtitle}


def get_trending(soup):
    """
    gets montreal gazette trending article pages

    args:
        soup (bs4 soup): the bs4 soup of the montreal gazette main news page
    """
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
                if (link.split('/')[1]!='news'):
                    continue
                # print (link.split('/')[1]!='news')
                headline = a_element.find("h3").text
                art["title"]=headline
                print("FETCHING: ", link)
                infos=get_art_info(link)

                art["publication_date"]=infos["pd"]
                art["author"]=infos["author"]
                art["blurb"]=infos["blurb"]
                # print("HEADLINE ",headline)
                # print("LINK ",link)
            articles.append(art)
    return articles

def save_json(infos: list,output: str):
    """
    saves a list of dictionaries to json

    args:
        infos (list): list containing the json dictionaries to save
        output (str): string of filename to save to
    """
    json_data = json.dumps(infos)
    with open(output, "w") as json_file:
        json_file.write(json_data)



if __name__=="__main__":
    glink="https://montrealgazette.com/category/news/"
    gaz=grab_html(glink)
    # print(gaz)
    arts=get_trending(gaz)
    output="trending.json"
    save_json(arts,output)