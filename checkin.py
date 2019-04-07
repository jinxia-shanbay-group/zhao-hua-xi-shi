# Run Env: python3 in Win or Linux
# you need to $pip3 install requests

# Use: modify the last part of script, replace the '*' with your true info,
# then use python3 ShanBei.py to run it

# if you want to auto run this script
# you can '$crontab -e' in the Linux Server terminal
# add '55 23 * * * python3 /home/local/ShanBei.py'
# that means the Server will auto run the script at 23:55 everyday

# Modified by voldikss 2019-04-07

import re
import requests
from config import USERNAME
from config import PASSWORD

file_object = open('dismissList.txt', 'w', encoding='utf-8')
dismiss_members = open('dismiss_members.txt', 'a', encoding='utf-8')


def login(username, password):
    login_url = 'https://www.shanbay.com/api/v1/account/login/web/'
    s = requests.Session()

    login_form_data = {'username': username,
                       'password': password,
                       }

    ress = s.put(login_url, data=login_form_data)
    return s


def kick_rule(name, check, age, rate, role, data_id):
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


def dismiss(s, data_id):
    url = 'http://www.shanbay.com/api/v1/team/member/'
    data = {
        'action': 'dispel',
        'ids': data_id
    }

    r = s.put(url, data=data)


def check(s):
    page = 1
    KickList = []
    flag = True
    cnt = 0
    while flag:

        url = 'https://www.shanbay.com/team/manage/?page='+str(page)+'#p1'
        members_list = s.get(url)
        res = members_list.text

        data_id = '<tr class="(.*?)" role="(.*?)" data-id="(.*?)"'

        link = '<a class="endless_page_link" href=(.*?) rel="page">&gt;&gt;</a>'

        pattern_age = '<td class="days">(.*?)</td>'

        pattern_rate = '<td class="rate">([\s\S]*?)<span class=(.*?)>(.*?)&#37'

        pattern_check = '<td class="checked(.*?)">([\s\S]*?)<span class="label label-(.*?)">'

        pattern_name = '<a class="nickname" href=(.*?)>(.*?)</a>'

        link_exist = re.findall(link, res)

        id_list = re.findall(data_id, res)

        check_list = re.findall(pattern_check, res)

        name_list = re.findall(pattern_name, res)

        age_list = re.findall(pattern_age, res)

        rate_list = re.findall(pattern_rate, res)

        for i in range(len(name_list)):
            name = name_list[i][1].strip()
            check = [check_list[2*i][2].strip(), check_list[2*i+1][2].strip()]
            age = age_list[i]
            rate = rate_list[i][2]
            role = id_list[i][1]
            data_id = id_list[i][2]
            print(data_id)
            cnt = cnt + 1
            if kick_rule(name, check, age, rate, role, data_id):
                KickList.append(data_id)
                file_object.write(name + '\n')

        if link_exist == []:
            flag = False
        else:
            page += 1

    print("cnt = " + str(cnt))
    print(KickList)

    for id_name in KickList:
        dismiss(s, id_name)
        #file_object.write(data_id + '\t'+ name + '\n')

    file_object.close()
    dismiss_members.write('    '.join(KickList))
    dismiss_members.write('\n')
    dismiss_members.close()


if __name__ == '__main__':
    s = login(USERNAME, PASSWORD)
    check(s)
