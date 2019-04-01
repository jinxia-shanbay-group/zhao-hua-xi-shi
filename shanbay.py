import logging
import os
import requests
import re
from bs4 import BeautifulSoup
from config import USERNAME
from config import PASSWORD


class Shanbay():
    def __init__(self, username, password):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
        }
        self.s = requests.Session()
        self.s.headers.update(headers)
        self.username = username
        self.password = password
        self.id_int = ""
        self.team_id = ""
        self.forum_id = ""

    def login(self):
        payload = {
            'account': self.username,
            'password': self.password
        }
        url = 'https://apiv3.shanbay.com/bayuser/login'
        res = self.s.post(url, json=payload)
        r_json = res.json()
        logging.info(f"[login result]: {r_json}")
        self.id_int = r_json['id_int']
        self.team_id = self.get_team()
        self.forum_id = self.get_forum_id()

    def get_team(self):
        """访问 我的空间 页面，拿到小组id"""
        html = self.s.get(f"https://web.shanbay.com/web/users/{self.id_int}/zone").text
        soup = BeautifulSoup(html, "lxml")

        # 没有加入小组
        try:
            href = soup.find(class_="team").find('a').get_attribute_list("href")[0]
            team_id = re.findall(r'detail/(\d+)/', href)[0]
            logging.info(f"[get team id]: {href}")
            return team_id
        except Exception as e:
            logging.error(f"[get team id failed]: {e}")
            return

    @property
    def team_url(self):
        # 必须要有 team_id
        assert self.team_id
        return f"https://www.shanbay.com/team/detail/{self.team_id}/"

    def get_forum_id(self):
        """ 获取我的小组的 forum_id 发帖回帖需要 """
        html = self.s.get(self.team_url).text
        soup = BeautifulSoup(html, "lxml")
        forum_id = soup.find(id='forum_id').attrs['value']
        logging.info(f"[forum id]: {forum_id}")
        return forum_id

    def get_thread(self, thread_id):
        """
        获取帖子情况，为了方便，不返回内容
        :return {
            "title": title,         帖子标题
            "threader": threader,   发帖人
            "content": content,     发帖内容
            "members": members      参与人员
        }
        """
        members = []
        for i in range(1,1000):
            thread_url = f"https://www.shanbay.com/team/thread/{self.team_id}/{thread_id}/?page={i}"
            res = self.s.get(thread_url)
            # only one page
            if res.status_code == 404:
                break

            html = res.text
            soup = BeautifulSoup(html, 'lxml')
            title = soup.find(id="threadtitle").text.strip()

            threads = soup.find_all(class_="post row")
            # content is only in the first page
            if i==1:
                content = threads[0].find(class_="post-content-todo").text.strip()
            for row in threads:
                nickname = row.find(class_="userinfo row").find(class_="span3").text.strip()
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
        """ 发帖 """
        data = {
            'title': title,
            'body': content,
            'csrfmiddlewaretoken': self.s.cookies.get('csrftoken')
        }
        url = f'https://www.shanbay.com/api/v1/forum/{self.forum_id}/thread/'
        res = self.s.post(url, data=data)
        r_json = res.json()
        logging.info(f"[new thread result]: {r_json}")

        return r_json["data"]['id']

    def set_thread(self, thread_id, attr):
        """ 设置帖子属性
        :param attr: sticky / starred / activity
        """
        url = f"https://www.shanbay.com/api/v1/team/{self.team_id}/thread/{thread_id}/"

        data = {
            "action": attr
        }

        res = self.s.put(url, data)
        r_json = res.json()
        logging.info(f"[set thread result]: {r_json}")

        return r_json['msg'] == "SUCCESS"

    def reply_thread(self, thread_id, content):
        """回复帖子"""
        url = f"https://www.shanbay.com/api/v1/forum/thread/{thread_id}/post/"
        data = {
            "csrfmiddlewaretoken": self.s.cookies.get("csrftoken"),
            "body": content
        }
        res = self.s.post(url, data)
        r_json = res.json()
        logging.info(f"[reply result]: {r_json}")

        return r_json['msg'] == "SUCCESS"


curr_path = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(curr_path, "task.log")

logging.basicConfig(filename=log_path,
                    level='INFO',
                    format="%(asctime)s %(filename)s [%(funcName)s] [line: %(lineno)d]  %(message)s",
                    filemode='w')

if __name__ == '__main__':
    sb = Shanbay(USERNAME, PASSWORD)
    sb.login()
    print(sb.id_int)
    print(sb.team_id)
    print(sb.forum_id)
    print(sb.get_thread("3138247"))
