from shanbay import Shanbay
from spider import Spider
from config import USERNAME
from config import PASSWORD
from task import Agent


def test_shanbay():
    sb = Shanbay(USERNAME, PASSWORD)
    sb.login()
    print(sb.id_int)
    print(sb.team_id)
    print(sb.forum_id)
    print(sb.get_thread("3128002"))


def test_spider():
    sp = Spider()
    print(sp.get_quote())
    print(sp.get_joke1())
    print(sp.get_joke2())


def test_task():
    """只能测试部分函数"""
    shanbay = Shanbay(USERNAME, PASSWORD)
    spider = Spider()
    agent = Agent(shanbay, spider)

    agent.thread_id = "3128002"
    agent.online_check()
    agent.local_record()
