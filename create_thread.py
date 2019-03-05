import datetime
import pytz
import random
from shanbay import Shanbay
from spider import Spider
from config import USERNAME
from config import PASSWORD


def foot():
    """构造帖子附加内容"""
    sp = Spider()
    methods = ["get_quote", "get_joke1", "get_joke2"]
    content = getattr(sp, methods[random.randint(0, 2)])()
    # body 部分每一行要加 >
    content["body"] = "\n\r\n\r".join(map(lambda s: "> " + s, content["body"].split("\n")))
    return content


def main():
    # 时区不一致
    tz = pytz.timezone("Asia/Shanghai")
    ct = datetime.datetime.now(tz)

    shanbay = Shanbay(USERNAME, PASSWORD)
    shanbay.login()

    title = ct.strftime("朝花惜时【%m.%d】🌸")
    content = "\n\r\n\r".join([
        "#>>【朝花惜时】打卡帖<<",
        "- **注意事项：**只有早上 5-8 点截图打卡才作数，其余不算哦～",
        "- **活动详情：** >>[点我了解](https://www.shanbay.com/team/thread/381970/3123197/)",
        "---",
        *foot().values()
    ])

    shanbay.new_thread(title, content)


if __name__ == '__main__':
    main()
