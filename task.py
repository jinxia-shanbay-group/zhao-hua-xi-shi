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
from config import QING_JIA


class Agent():
    def __init__(self, shanbay, spider):
        self.shanbay = shanbay
        self.spider = spider
        # 初始化时候就登录
        self.shanbay.login()
        # 新帖子的id
        self.thread_id = ""

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
            logging.error(f"build foot content successfully")
            return foot
        except Exception as e:
            logging.error(f"build foot content failed: {e}")
            return None

    @property
    def ctime(self):
        """获取当前时区的时间"""
        tz = pytz.timezone("Asia/Shanghai")
        ct = datetime.datetime.now(tz)
        return ct

    def create_thread(self):
        """创建打卡帖"""
        title = self.ctime.strftime("🌸朝花惜时【%m.%d】")
        content = "\n\r\n\r".join([
            "# >>朝花惜时打卡帖<<",
            "- **注意事项：**只有早上 5-8 点截图打卡才作数，其余不算哦～",
            "- **活动详情：** >>[点我了解](https://www.shanbay.com/forum/thread/3137629/)",
            *self.add_foot()
        ])

        self.thread_id = self.shanbay.new_thread(title, content)
        logging.info(f"create a new thread: {self.thread_id}")
        time.sleep(0.5)
        self.shanbay.set_thread(self.thread_id, "activity")

    def online_check(self):
        """ 检查打卡情况 """
        thread = self.shanbay.get_thread(self.thread_id)
        result = {}
        for m in MEMBERS:
            if m in QING_JIA:
                result[m] = 2
            elif m in thread['members']:
                result[m] = 1
            else:
                result[m] = 0
        return result

    def local_record(self, result):
        """将查卡情况写进 markdown 文件"""
        """There must be some improvements"""
        checkin_logfile = self.ctime.strftime(
            os.path.join(checkin_log_path, "%Y-%m.md"))

        if not os.path.exists(checkin_logfile):
            header = "|".join(["",
                               "date",
                               *result.keys(),
                               "\n"
                               ])
            necker = "|".join(["",
                               *["---"] * (len(result)+1),
                               "\n"
                               ])
            with open(checkin_logfile, 'w') as f:
                f.write(header)
                f.write(necker)

        with open(checkin_logfile, 'r') as f:
            line = f.readline().strip()
            names = list(map(lambda x: x.strip(), line.split("|")[2:-1]))

        # 0：缺卡，1: 打卡，2：请假
        flag = ["❌", "✔️ ", "🚫"]
        # 每个人的打卡状态 {"who":True/False, ...}
        status = [result.get(n) for n in names]
        print(status)

        record = "|".join(["",
                           self.ctime.strftime("%m/%d"),
                           *[flag[s] for s in status],
                           "\n"
                           ])

        with open(checkin_logfile, 'a') as f:
            f.write(record)

    def git_pull(self):
        "pull first"
        cmd = f"cd {checkin_log_path} && git pull -f"
        os.popen(cmd)

    def git_push(self):
        """push 到 GitHub"""
        date = self.ctime.strftime("%Y-%m-%d")
        cmd = f"cd {checkin_log_path} && git add . && git commit -m 'checkin log: {date}' && git push -f"
        p = os.popen(cmd)
        msg = p.read()
        logging.info(f"git push result: {msg}")
        p.close()

    def online_report(self, result):
        """在当日的帖子下回复总结"""
        if 0 in result.values():
            count = len(result.values()) - sum(result.values())
            content = f"遗憾，有{count}位同学未完成打卡。"
        else:
            content = "全体完成打卡，撒花～"
        content = f"今日活动报告：\n\r\n\r{content}"

        self.shanbay.reply_thread(self.thread_id, content)


curr_path = os.path.dirname(os.path.abspath(__file__))
checkin_log_path = os.path.join(curr_path, "../zhao-hua-xi-shi-checkin-log")
logfile = os.path.join(curr_path, "task.log")

logging.basicConfig(filename=logfile,
                    level='INFO',
                    format="%(asctime)s %(filename)s [%(funcName)s] [line: %(lineno)d]  %(message)s",
                    filemode='a')

if __name__ == '__main__':
    # 发帖
    shanbay = Shanbay(USERNAME, PASSWORD)
    spider = Spider()
    agent = Agent(shanbay, spider)
    agent.create_thread()

    # 5:00 - 8:00
    time.sleep(3600 * 3 + 10)

    # 查卡
    result = agent.online_check()
    agent.online_report(result)
    agent.git_pull()
    agent.local_record(result)
    agent.git_push()
