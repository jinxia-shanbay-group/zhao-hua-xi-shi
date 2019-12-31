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
        self._username = username
        self._password = password
        self.user_id = ""
        self.team_id = ""
        self.forum_id = ""

    def login(self):
        payload = {
            'account': self._username,
            'password': self._password
        }
        url = 'https://apiv3.shanbay.com/bayuser/login'
        res = self.s.post(url, json=payload)
        r_json = res.json()
        logging.info(f"login as {r_json['username']}")
        self.user_id = r_json['id_int']
        self.team_id = self._get_team_id()
        self.forum_id = self._get_forum_id()

    def login_by_cookies():
        ...

    def _get_team_id(self):
        """访问 我的空间 页面，拿到小组id"""
        url = f"https://web.shanbay.com/web/users/{self.user_id}/zone"
        html = self.s.get(url).text
        soup = BeautifulSoup(html, "lxml")

        # 没有加入小组
        try:
            href = soup.find(class_="team").find('a')\
                .get_attribute_list("href")[0]
            team_id = re.findall(r'detail/(\d+)/', href)[0]
            logging.info(f"get team id: {team_id}")
            return team_id
        except Exception as e:
            logging.error(f"get team id failed: {e}")
            return

    @property
    def team_url(self):
        # 必须要有 team_id
        team_id = self.team_id or self._get_team_id()
        return f"https://www.shanbay.com/team/detail/{team_id}/"

    def _get_forum_id(self):
        """ 获取我的小组的 forum_id 发帖回帖需要 """
        html = self.s.get(self.team_url).text
        soup = BeautifulSoup(html, "lxml")
        forum_id = soup.find(id='forum_id').attrs['value']
        logging.info(f"get forum id: {forum_id}")
        return forum_id

    def get_thread(self, thread_id):
        """
        获取帖子情况，为了方便，不返回内容
        :return
        {
            "title": title,         帖子标题
            "threader": threader,   发帖人
            "content": content,     发帖内容
            "members": members      参与人员
        }
        """
        members = []
        for i in range(1, 1000):
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
            if i == 1:
                content = threads[0].find(
                    class_="post-content-todo").text.strip()
            for row in threads:
                nickname = row.find(class_="userinfo row").find(
                    class_="span3").text.strip()
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
        thread_id = r_json['data']['id']
        logging.info(f"new thread: {thread_id}")
        return thread_id

    def set_thread(self, thread_id, attr):
        """
        设置帖子属性
        :param attr: sticky / starred / activity
        """
        url = f"https://www.shanbay.com/api/v1/team/{self.team_id}/thread/{thread_id}/"
        data = {"action": attr}
        res = self.s.put(url, data)
        r_json = res.json()
        if r_json['msg'] == 'SUCCESS':
            logging.info(f"set thread attribute to: {attr}")
            return True
        else:
            logging.info(f"set thread attribute failed")
            return False

    def reply_thread(self, thread_id, content):
        """回复帖子"""
        url = f"https://www.shanbay.com/api/v1/forum/thread/{thread_id}/post/"
        data = {
            "csrfmiddlewaretoken": self.s.cookies.get("csrftoken"),
            "body": content
        }
        res = self.s.post(url, data)
        r_json = res.json()
        if r_json['msg'] == 'SUCCESS':
            logging.info(f"reply thread {thread_id} successfully")
            return True
        else:
            logging.info(f"reply thread failed")
            return False

    def _dissmiss(self, user_id):
        """ 踢人 """
        url = 'http://www.shanbay.com/api/v1/team/member/'
        data = {
            'action': 'dispel',
            'ids': user_id
        }
        self.s.put(url, data=data)

    def kick_rule(self, check, age, rate, role):
        """ 踢人规则 """
        if role != "2":
            return False
        elif int(age) <= 3 and check[1] == 'important':
            return True
        elif int(age) <= 7 and check == ['important', 'important']:
            return True
        elif float(rate) < 85.0:
            return True
        elif float(rate) < 95.0:
            return True and check == ['important', 'important']
        return False

    def check(self):
        """查卡+踢人"""
        page = 1
        kick_members = {}
        flag = True
        while flag:
            url = f'https://www.shanbay.com/team/manage/?page={page}#p1'
            members_list = self.s.get(url)
            res = members_list.text

            data_id = '<tr class="(.*?)" role="(.*?)" data-id="(.*?)"'
            link = '<a class="endless_page_link" href=(.*?) rel="page">&gt;&gt;</a>'
            pattern_age = '<td class="days">(.*?)</td>'
            pattern_rate = r'<td class="rate">([\s\S]*?)<span class=(.*?)>(.*?)&#37'
            pattern_check = r'<td class="checked(.*?)">([\s\S]*?)<span class="label label-(.*?)">'
            pattern_name = '<a class="nickname" href=(.*?)>(.*?)</a>'
            link_exist = re.findall(link, res)
            id_list = re.findall(data_id, res)
            check_list = re.findall(pattern_check, res)
            name_list = re.findall(pattern_name, res)
            age_list = re.findall(pattern_age, res)
            rate_list = re.findall(pattern_rate, res)

            for i in range(len(name_list)):
                name = name_list[i][1].strip()
                check = [check_list[2*i][2].strip(), check_list[2*i+1]
                         [2].strip()]
                age = age_list[i]
                rate = rate_list[i][2]
                role = id_list[i][1]
                data_id = id_list[i][2]
                if self.kick_rule(check, age, rate, role):
                    kick_members[data_id] = name

            if link_exist == []:
                flag = False
            else:
                page += 1

        for id in kick_members:
            self._dissmiss(id)
        logging.info(f"kicked out: {', '.join(kick_members.values())}")


curr_path = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(curr_path, "task.log")

logging.basicConfig(filename=log_path,
                    level='INFO',
                    format="%(asctime)s %(filename)s [%(funcName)s] [line: %(lineno)d]  %(message)s",
                    filemode='a')

if __name__ == '__main__':
    sb = Shanbay(USERNAME, PASSWORD)
    sb.login()
    print(sb.user_id)
    print(sb.team_id)
    print(sb.forum_id)
    # print(sb.get_thread("3138247"))
    # sb.check()
