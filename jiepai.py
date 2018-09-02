import  requests
import pymongo
import json
import re
from bs4 import BeautifulSoup
import os
import hashlib
headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}
def get_page_index(offset,keyword):
    url="https://www.toutiao.com/search_content/"
    para={
        "offset": offset,
        "format": "json",
        "keyword": keyword,
        "autoload": True,
        "count": 20,
        "cur_tab": 1,
        "from": "gallery"
    }
    content=requests.get(url,params=para).content

    for data in json.loads(content)["data"]:
        if "article_url" in data.keys():
             article_url=data["article_url"]
             yield article_url

def get_page_detail(url):
    print(url)
    response = requests.get(url,headers=headers)
    if response.status_code == 200:  # 即能够正常请求网络，我们就对网络url进行抓取
        content=response.text
        soup=BeautifulSoup(content,"lxml")
        title=soup.select("title")[0].text
        images_pattern = re.compile('gallery: JSON.parse\((.*?)\)', re.S)
        images = re.search(images_pattern, content)
        images = json.loads(images.group(1))  # json.loads 不能转换单引号数据类型,json对象。
        for item in json.loads(images)["sub_images"]:
            yield  {"title":title,"imageurl":item["url"]}
def download_gallery(result):
    title=result["title"]
    path=title
    if not os.path.exists(title):
        os.mkdir(title)
    url=result["imageurl"]
    resp=requests.get(url)
    filename=hashlib.md5(url.encode(encoding='utf-8')).hexdigest()+".jpg"
    with open(os.path.join(path,filename),"wb") as f:
        f.write(resp.content)


def save(result):
        conn = pymongo.MongoClient("192.168.11.129",27017)
        db = conn["test"]  #连接mydb数据库，没有则自动创建
        collec=db.jiepai
        if collec.insert(result):
            print("inserted into MongoDB")
            return  True
        return False


if __name__=="__main__":
    for offset in [i*20 for i in range(20)]:
        urls=get_page_index(offset,"街拍")
        for url in urls:
            result=get_page_detail(url)
            for imageurl in result:
                save(imageurl)
                download_gallery(imageurl)

