import requests
import os
from bs4 import BeautifulSoup
from tldextract import extract


class Spider():
    def __init__(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
        }
        self.s = requests.Session()
        self.s.headers.update(headers)

    def get_quote(self):
        """获取扇贝首页的每日格言"""
        quote_url = "https://rest.shanbay.com/api/v2/quote/quotes/today/"
        q_json = self.s.get(quote_url).json()
        head = "# >>Quote of The Day<<"
        neck = f"*from: {q_json['data']['author'].strip()}*"
        body = q_json['data']['content']+'\n' + q_json['data']['translation']
        # body 部分每一行要加 >
        body = "\n\r\n\r".join(map(lambda s: "> " + s, body.split("\n")))

        return {
            "head": head,
            "neck": neck,
            "body": body
        }

    def get_joke(self):
        """获取每日笑话"""
        joke_url = "https://icanhazdadjoke.com/"
        domain = extract(joke_url).domain
        head = "# >>Joke of The Day<<"
        neck = f"*from [{domain}]({joke_url})*"

        html = self.s.get(joke_url).text
        soup = BeautifulSoup(html, "lxml")
        body = soup.find(class_="card-content").text.strip()
        # body 部分每一行要加 >
        body = "\n\r\n\r".join(map(lambda s: "> " + s, body.split("\n")))

        return {
            "head": head,
            "neck": neck,
            "body": body
        }

    def get_pic(self):
        pic_url = "https://picsum.photos/1920/1080/?random"
        head = "# >>Photo of The Day<<"
        neck = "*from [picsum.photos](https://picsum.photos)*"

        res = self.s.get(pic_url)
        href = res.url
        body = f"![]({href})"

        return {
            "head": head,
            "neck": neck,
            "body": body
        }


if __name__ == '__main__':
    sp = Spider()
    print(sp.get_quote())
    print(sp.get_joke())
    print(sp.get_pic())
