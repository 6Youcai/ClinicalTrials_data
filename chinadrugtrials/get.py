import requests
from bs4 import BeautifulSoup
import time

def internet(page = 1):
    url = "http://www.chinadrugtrials.org.cn/eap/clinicaltrials.searchlist"
    info = {"currentpage": page, "pagesize": 40}
    chrome = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"}
    web = requests.post(url, data = info, headers = chrome)
    return web

def analysis(html, f):
    soup = BeautifulSoup(html, features = "lxml")
    searchfrm = soup.find_all(id = 'searchfrm')
    table = searchfrm[0].find_all('table')[2]
    rows = table.find_all('tr')
    for line in rows[1:]:
        col = line.find_all('td')
        id = col[1].a['id']
        cells = map(lambda x: x.text.strip(), col)
        text = "\t".join(cells) + '\t' + id + '\n'
        f.write(text)

def main():
    all_pages = 161
    out = open("chinadrugtrials.txt", 'w')
    for i in range(1, all_pages + 1):
        web = internet(i)
        if web.ok:
           analysis(web.text, out)
        else:
            print("Failed:", i)
        time.sleep(10)

if __name__ == "__main__":
    main()
