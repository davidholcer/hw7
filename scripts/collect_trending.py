#lotsa imports
from bs4 import BeautifulSoup
import codecs
import re
import json
import requests
import logging
import time
import os
from datetime import datetime, timedelta
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument(
    "-o", "--output", required=True, help="the input json file name"
)
parser.add_argument(
    "-c", "--cache", required=False, help="whether or not to use/save cache", default=True
)
parser.add_argument(
    "-d", "--days", required=False, help="max cache date before rewriting to cache", default=1
)

args = parser.parse_args()

logger=logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)

def get_html(site:str,cache:bool,stale:int):
    if cache==False:
        soup=grab_html(site, cache,homepage=True)
    else:
        news_out="../data/news.html"
        old=False
        try:
            mod_time = os.path.getmtime(news_out)
        except FileNotFoundError:
            soup=grab_html(site,cache,homepage=True)
        else:
            # Convert the timestamp to a datetime object
            md = datetime.fromtimestamp(mod_time)
            # Get the current datetime
            cd = datetime.now()
            # Calculate the time difference
            td = cd - md
            # Check if the time difference is more than one day (24 hours)
            old = td > timedelta(days=stale)
        if old:
            soup=grab_html(site, cache)
        else:
            with open(news_out, 'r') as f:
                raw_soup=f.read()
                soup = BeautifulSoup(raw_soup,features="html.parser")
    return soup

def grab_html(site:str,cache:bool,homepage:bool=False):
    """
    gets bs4 soup of site by using requests

    args:
        site (str): the site url to fetch
    """
    # print("GRABBING HTML FROM {}\n".format(site))
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    result = requests.get(site, headers=headers)
    result=result.content.decode()
    soup = BeautifulSoup(result,features="html.parser")
    #save soup to file news.html if caching
    if cache and homepage:
        news_out="../data/news.html"
        with open(news_out, "w") as f:
            f.write(result)  
    return soup

def get_art_info(site:str,cache:bool,stale:int):
    arts="../data/art_infos.json"
    if not cache:
        infos=grab_art_info(site, cache)
    else:
        #read file as list, check if link matches, check time cached
        # print("CHECKIN ART CACHE")
        if not os.path.isabs(arts):
            arts = os.path.abspath(arts)
        if not os.path.exists(arts):
            # print("NOT EXISTS")
            infos=grab_art_info(site,cache)
        else:
            with open(arts, "r") as f:
                art_list = json.load(f)
            # Iterate over 'art_list' to filter out old items
            cd = datetime.now()
            art_list = [item for item in art_list if (cd - datetime.fromtimestamp(item["time_cached"])) <= timedelta(days=stale)]
            with open(arts, "w") as f:
                json.dump(art_list, f, indent=4)
            found=False
            for item in art_list:
                if item.get("site") == site:
                    found=True
                    infos=item
            if not found:
                infos=grab_art_info(site, cache)
    return infos

def cache_info(infos):
    ct = datetime.now().timestamp()
    infos["time_cached"] = ct

    a_infos = "../data/art_infos.json"

    if not os.path.exists(a_infos):
        art_init = [infos]  # Start with a list containing the first info
        with open(a_infos, "w") as f:
            json.dump(art_init, f, indent=4)
    else:
        # Read the existing data from the file
        with open(a_infos, "r") as jsF:
            existing_data = json.load(jsF)

        existing_data.append(infos)  # Add the new info to the list

        # Write the updated list of infos back to the file
        with open(a_infos, "w") as f:
            json.dump(existing_data, f, indent=4)
    return infos

def grab_art_info(site:str,cache:bool):
    """
    gets montreal gazette article page info using bs4 soup dump

    args:
        site (str): the site url to get the info of
    """
    NEWS_QUERY_STRING_TEMPLATE="https://montrealgazette.com{}"
    query_string=NEWS_QUERY_STRING_TEMPLATE.format(site)

    soup=grab_html(query_string,cache)
    
    # Get the text of p element with class "article-subtitle"
    article_subtitle = soup.find('p', class_='article-subtitle').text

    # Get the text of span element with class "published-by__author"
    title=soup.find('h1',class_='article-title').text
    author = soup.find('span', class_='published-by__author')
    if (not author):
        author = soup.find('div', class_='wire-published-by__company')
    author=author.text

    # Get the text of span element with class "published-date__since"
    published_date = soup.find('span', class_='published-date__since').text

    infos={"title":title, "pd": published_date.lstrip().rstrip(), "author": author.lstrip().rstrip(), "blurb": article_subtitle.lstrip().rstrip(),"site":site}

    # infos={"title":"abc","pd":"123","author":"me","blurb":"blurb","site":"site"}
    if cache: cache_info(infos)
    return infos

def get_trending(soup,cache,stale):
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
                if (link.split('/')[1]=='gallery'):
                    continue
                #.lstrip and .rstrip remove leading and trailing whitespaces

                #check if link is cached 
                #sets boolean to see if link is cached dt (default 24 h) ago
                #cached=false
                
                #fetch info w/ cache state
                # print("FETCHING: ", link)
                infos=get_art_info(link,cache,stale)
                # print(infos)

                # headline = a_element.find("h3").text.lstrip().rstrip()
                # art["title"]=headline.lstrip()
                art["title"]=infos["title"]
                art["publication_date"]=infos["pd"]
                art["author"]=infos["author"]
                art["blurb"]=infos["blurb"]
            articles.append(art)
    return articles

def save_json(infos: list,output: str):
    """
    saves a list of dictionaries to json

    args:
        infos (list): list containing the json dictionaries to save
        output (str): string of filename to save to
    """
    json_data = json.dumps(infos, indent=4)
    
    with open(output, "w") as json_file:
        json_file.write(json_data)

def combo(output):
    """
    runs the combo of functions to save the output json of trending news articles from the montreal gazette

    args: output(str): output json file to write out
    """
    args.days=int(args.days)
    args.cache = True if args.cache == "True" else False
    glink="https://montrealgazette.com/category/news/"
    gaz=get_html(glink,args.cache,args.days)
    arts=get_trending(gaz,args.cache,args.days)
    save_json(arts,output)

if __name__=="__main__":
    combo(args.output)