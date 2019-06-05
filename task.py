import datetime
import time
import pytz
import random
import logging
import os
from shanbay import Shanbay
from spider import Spider
from config import USERNAME
from config import PASSWORD
from config import MEMBERS


class Agent():
    def __init__(self, shanbay, spider):
        self.shanbay = shanbay
        self.spider = spider
        # 初始化时候就登录
        self.shanbay.login()
        # 新帖子的id
        self.thread_id = ""
        # 成员打卡情况
        self.status = {}
        # 总体情况
        self.all_status = False

    def add_foot(self):
        """构造帖子附加内容"""
        try:
            foot = [
                "---",
                *self.spider.get_quote().values(),
                "---",
                *self.spider.get_joke().values(),
                "---",
                *self.spider.get_pic().values()
            ]
        except Exception as e:
            foot = []
            logging.error(f"[build foot content failed]: {e}")
        return foot

    @property
    def ctime(self):
        """获取当前时区的时间"""
        tz = pytz.timezone("Asia/Shanghai")
        ct = datetime.datetime.now(tz)
        return ct

    def create_thread(self):
        """创建打卡帖"""
        title = self.ctime.strftime("朝花惜时【%m.%d】")
        content = "\n\r\n\r".join([
            "# >>朝花惜时打卡帖<<",
            "- **注意事项：**只有早上 5-8 点截图打卡才作数，其余不算哦～",
            "- **活动详情：** >>[点我了解](https://www.shanbay.com/forum/thread/3137629/)",
            *self.add_foot()
        ])

        self.thread_id = self.shanbay.new_thread(title, content)
        logging.info(f"[thread id]: {self.thread_id}")
        time.sleep(0.5)
        self.shanbay.set_thread(self.thread_id, "activity")

    def online_check(self):
        """ 检查打卡情况 """
        members = self.shanbay.get_thread(self.thread_id)['members']
        self.status = {m: m in members for m in MEMBERS}
        self.all_status = all(self.status.values())
        # 查卡结果
        logging.info(f"[check result]: {self.status}")

    def local_record(self):
        """将查卡情况写进 markdown 文件"""
        checkin_logfile = self.ctime.strftime(
            os.path.join(checkin_log_path, "%Y-%m.md"))

        if not os.path.exists(checkin_logfile):
            header = "|".join(["",
                               "date",
                               *self.status.keys(),
                               "\n"
                               ])
            necker = "|".join(["",
                               *["---"] * (len(self.status)+1),
                               "\n"
                               ])
            with open(checkin_logfile, 'w') as f:
                f.write(header)
                f.write(necker)

        with open(checkin_logfile, 'r') as f:
            line = f.readline().strip()
            names = list(map(lambda x: x.strip(), line.split("|")[2:-1]))

        flag = {True: "✔️", False: "❌"}
        # 每个人的打卡状态 {"who":True/False, ...}
        result = [self.status.get(n) for n in names]

        record = "|".join(["",
                           self.ctime.strftime("%m/%d"),
                           *[flag[s] for s in result],
                           "\n"
                           ])

        with open(checkin_logfile, 'a') as f:
            f.write(record)

    def git_pull(self):
        "pull first"
        cmd = f"cd {checkin_log_path} && git pull origin master"
        os.popen(cmd)

    def git_push(self):
        """push 到 GitHub"""
        date = self.ctime.strftime("%Y-%m-%d")
        cmd = f"cd {checkin_log_path} && git add . && git commit -m 'checkin log: {date}' && git push --force --all"
        p = os.popen(cmd)
        msg = p.read()
        logging.info(f"[git push result]: {msg}")
        p.close()

    def online_report(self):
        """在当日的帖子下回复总结"""
        if self.all_status:
            content = "全体完成打卡，撒花～"
        else:
            count = len(self.status.values()) - sum(self.status.values())
            content = f"遗憾，有{count}位同学未完成打卡。"
        content = f"今日活动报告：\n\r\n\r{content}"

        self.shanbay.reply_thread(self.thread_id, content)


curr_path = os.path.dirname(os.path.abspath(__file__))
checkin_log_path = os.path.join(curr_path, "../zhao-hua-xi-shi-checkin-log")
logfile = os.path.join(curr_path, "task.log")

logging.basicConfig(filename=logfile,
                    level='INFO',
                    format="%(asctime)s %(filename)s [%(funcName)s] [line: %(lineno)d]  %(message)s",
                    filemode='w')

if __name__ == '__main__':
    # 发帖
    shanbay = Shanbay(USERNAME, PASSWORD)
    spider = Spider()
    agent = Agent(shanbay, spider)
    agent.create_thread()

    # 5:00 - 8:00
    time.sleep(3600 * 3 + 10)

    # 查卡
    agent.online_check()
    agent.online_report()
    agent.git_pull()
    agent.local_record()
    agent.git_push()
