from shanbay import Shanbay
from config import USERNAME
from config import PASSWORD
from config import MEMBERS


def online_check(thread):
    """
    检查打卡情况
    :param thread:
    :return:
    """
    shanbay = Shanbay(USERNAME, PASSWORD)
    shanbay.login()
    result = shanbay.get_thread(thread)
    fail = [m for m in MEMBERS if not m in result]
    status = len(fail) == 0
    return {
        "status": status,
        "fail": fail
    }


def local_record():
    """
    write the result to the markdown file and push it to GitHub
    :return:
    """
    ...
