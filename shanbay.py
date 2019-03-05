import requests
import re
from bs4 import BeautifulSoup
from config import USERNAME
from config import PASSWORD


class Shanbay():
    def __init__(self, username, password):
        """
        :param username:
        :param password:
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
        }
        self.s = requests.Session()
        self.s.headers.update(headers)
        self.username = username
        self.password = password
        self.id_int = None

    def login(self):
        """
        :param username:
        :param password:
        :return: True or False
        """
        payload = {
            'account': self.username,
            'password': self.password
        }
        url = 'https://apiv3.shanbay.com/bayuser/login'
        res = self.s.post(url, json=payload)
        r_json = res.json()
        self.id_int = r_json['id_int']

    @property
    def team_url(self):
        html = self.s.get(f"https://web.shanbay.com/web/users/{self.id_int}/zone").text
        soup = BeautifulSoup(html, "lxml")
        team_url = soup.find(class_="team").find('a').get_attribute_list("href")[0]
        return team_url

    @property
    def team_id(self):
        return re.findall(r'detail/(\d+)/', self.team_url)[0]

    def forum_id(self):
        """
        获取我的小组的 forum_id 发帖回帖需要
        :refer: https://github.com/mozillazg/python-shanbay
        :return:
        """
        html = self.s.get(self.team_url).text
        soup = BeautifulSoup(html)
        return soup.find(id='forum_id').attrs['value']

    def get_thread(self, thread_id):
        """
        获取帖子情况，为了方便，不返回内容
        :param id:
        :return {
            "title": title,         帖子标题
            "threader": threader,   发帖人
            "content": content,     发帖内容
            "members": members      参与人员
        }
        """
        thread_url = f"https://www.shanbay.com/team/thread/{self.team_id}/{thread_id}/"
        html = self.s.get(thread_url).text
        soup = BeautifulSoup(html, 'lxml')
        title = soup.find_all(id="threadtitle")[0].text.strip()

        threads = soup.find_all(class_="post row")
        content = threads[0].find_all(class_="post-content-todo")[0].text.strip()
        members = []
        for row in threads:
            nickname = row.find_all(class_="userinfo row")[0].find_all(class_="span3")[0].text.strip()
            if not nickname in members:
                members.append(nickname)

        threader, members = members[0], members[1:]

        return {
            "title": title,
            "threader": threader,
            "content": content,
            "members": members
        }

    def new_thread(self, title, content):
        """
        发帖
        :param forum_id:
        :param title:
        :param content:
        :return:
        """
        data = {
            'title': title,
            'body': content,
            'csrfmiddlewaretoken': self.s.cookies.get('csrftoken')
        }
        url = f'https://www.shanbay.com/api/v1/forum/{self.forum_id()}/thread/'
        r = self.s.post(url, data=data)
        j = r.json()

        print(r.json())
        # todo
        # if j['status_code'] == 0:
        #     return j['data']['thread']['id']

    def set_thread(self, thread_id, attr):
        """
        设置帖子属性
        :param thread_id:
        :param attr: sticky / starred / activity
        :return:
        """
        url = f"https://www.shanbay.com/api/v1/team/{self.team_id}/thread/{thread_id}/"
        data = {
            "action": attr
        }

        res = self.s.put(url, data)
        r_json = res.json()

        return r_json['msg'] == "SUCCESS"

    def reply_thread(self, thread_id):
        ...


if __name__ == '__main__':
    sb = Shanbay(USERNAME, PASSWORD)
    sb.login()
    print(sb.team_url)

    # th = sb.get_thread("3127549")
    # print(th)
