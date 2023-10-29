from pathlib import Path
import requests

def get_html_data():
    fpath =Path("../data") / "news.html"

    if not fpath.exists():
        data=requests.get(f"https://montrealgazette.com/category/news/")
    
        with open (fpath, "w") as f:
            f.write(data.text)
    
    with open(fpath) as f:
        return f.read()
    
def main():
    html_data=get_html_data()
    print(html_data)

if __name__=="__main__":
    main()

