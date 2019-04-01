# zhao-hua-xi-shi

### About
[忽而今夏](https://www.shanbay.com/team/detail/381970/)扇贝小组【朝花惜时】活动相关

- [`check_log`](./check_log): 每月活动打卡记录
- [`config.py`](./config.py): 配置文件
- [`shanbay.py`](./shanbay.py): Shanbay 类，提供扇贝网操作
- [`spider.py`](./spider.py): Spider 类，抓取简要 Joke/Quote
- [`task.py`](./task.py): Agent 类，用于每日发帖，查卡并记录，提交

### Usage

- Clone the two repositories to the same directory
    - [zhao-hua-xi-shi](https://github.com/jinxia-shanbay-group/zhao-hua-xi-shi)
    - [zhao-hua-xi-shi-checkin-log](https://github.com/jinxia-shanbay-group/zhao-hua-xi-shi-checkin-log)

- Install deps
    ```
    pip3 install -r requirements.txt
    ```

- Configure

    use [`config_tmpl.py`](./config_tmpl.py) to configure and rename it to `config.py`.

- Use `crontab`
