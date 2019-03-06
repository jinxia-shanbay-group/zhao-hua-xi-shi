import requests
from bs4 import BeautifulSoup
from tldextract import extract

joke_url1 = "https://icanhazdadjoke.com/"
joke_url2 = "https://goodriddlesnow.com/jokes/random"
quote_url = "https://rest.shanbay.com/api/v2/quote/quotes/today/"


class Spider():
    def __init__(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
        }
        self.s = requests.Session()
        self.s.headers.update(headers)

    def get_quote(self):
        """获取扇贝首页的每日格言"""
        q_json = self.s.get(quote_url).json()
        head = "# >>Quote of The Day<<"
        neck = f"*author: {q_json['data']['author']}*"
        body = q_json['data']['content']

        return {
            "head": head,
            "neck": neck,
            "body": body
        }

    def get_joke1(self):
        """获取每日笑话"""
        domain = extract(joke_url1).domain
        head = "# >>Joke of The Day<<"
        neck = f"*from [{domain}]({joke_url1})*"

        html = self.s.get(joke_url1).text
        soup = BeautifulSoup(html, "lxml")
        body = soup.find(class_="card-content").text.strip()

        return {
            "head": head,
            "neck": neck,
            "body": body
        }

    def get_joke2(self):
        """获取每日笑话"""
        domain = extract(joke_url2).domain
        head = "# >>Joke of The Day<<"
        neck = f"*from [{domain}]({joke_url2})*"

        html = self.s.get(joke_url2).text
        soup = BeautifulSoup(html, "lxml")
        jq = soup.find(class_="joke-question").text.strip()
        ja = soup.find(class_="joke-answer").text.strip()

        if "Punch line" in ja:
            body = jq + "\n" + ja
        else:
            body = jq

        return {
            "head": head,
            "neck": neck,
            "body": body
        }


if __name__ == '__main__':
    sp = Spider()
    print(sp.get_quote())
    print(sp.get_joke1())
    print(sp.get_joke2())
