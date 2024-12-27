from playwright.sync_api import sync_playwright
import random
import time
import json
import os
import sys
import re
import math

from generate_words import main as generate_words
from generate_words import main2 as generate_words_weibo
from check_points import main as check_points
from extra_points import get_extra_points

import requests

_pc_count = 0
_phone_count = 0


def read_random_line(file_path: str) -> str:
    """
    Read a random line from a file, remove the newline character at the end of the line and return it.

    Args:
        file_path (str): The path of the file to read.

    Returns:
        str: The random line read from the file.

    """
    with open(file_path, 'r', encoding="utf8") as file:
        lines = file.readlines()
        return random.choice(lines).removesuffix('\n')


def get_random_sleep_time() -> int:
    """
    Get a random integer between 10 and 20.
    """
    return random.randint(10, 30)


def do_feishu_webhook(msg: str) -> None:
    """
    Send a message to Feishu using a webhook.

    It reads the webhook from a file named ".feishu" in the current directory which should contain the webhook URL.
    If the file does not exist, it will not send the message, and it will not raise any exceptions.

    Args:
        msg (str): The message to send.

    """
    if os.path.exists(".feishu"):
        with open(".feishu", "r", encoding="utf8") as f:
            webhook = f.read()
            requests.post(webhook, json={
                "msg_type": "text",
                "content": {
                    "text": msg
                }
            })


def fsprint(msg):
    """
    Print a message and send it to Feishu using a webhook.

    Just a wrapper around `print()` and `do_feishu_webhook()`, refer to their documentation for more information.

    Args:
        msg (str): The message to print and send.

    """
    print(msg)
    do_feishu_webhook(msg)


def main(times: int, do_phone: bool = False, show_countdown: bool = True, bypass: bool = False):
    """
    Main function to stimulate the Bing search using Playwright.

    This function will open a browser, load the Bing homepage, check the login status, and cache the cookies.
    Then it will search for random words for the specified times.

    It will create `.headless` and `cookies.json` files to store the headless mode status and cookies respectively for PC Stimulator.
    For Phone Stimulator, it will create `.headless_phone` and `cookies_phone.json` files.

    For the first time, it will require manual login and confirmation, then it will cache the cookies and set the headless mode status.
    PC Stimulator and Phone Stimulator will have separate cookies and headless mode status, they need to be generated separately.

    Args:
        times (int): The number of times to search.
        do_phone (bool): Whether to use the Phone Stimulator, default is False.
        show_countdown (bool): Whether to show the countdown when waiting, default is True. This option is designed for cron jobs.
        bypass (bool): Whether to bypass the checking for if user is logged in, and keep the headless mode on, default is False.

    Raises:
        TypeError: If the browser failed to load or the page failed to load, or the cookies failed.
    """

    global _pc_count
    global _phone_count

    # Switch between PC and Phone Stimulator
    _headless = '.headless'
    _cookies = 'cookies.json'
    if do_phone:
        _headless = '.headless_phone'
        _cookies = 'cookies_phone.json'

    # Load headless mode status
    if os.path.exists(_headless):
        with open(_headless, "r", encoding="utf8") as f:
            headless = bool(int(f.read()))
    else:
        headless = False

    headless = headless or bypass

    if headless:
        print("将使用无头模式")

    # Main process
    with sync_playwright() as p:

        # Load cookies if exists
        if os.path.exists(_cookies):
            print("已检测到cookies文件, 正在加载cookies...")
            with open(_cookies, "r", encoding="utf8") as f:
                cookies = json.load(f)

        # Lauch browser depending on headless mode, setting user agent and viewport for Phone Stimulator, then create a new page
        browser = p.chromium.launch(
            headless=headless
        )

        if do_phone:
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36 EdgA/123.0.0.0",
                viewport={"width": 360, "height": 640},
                is_mobile=True,
                has_touch=True,
                locale="zh-CN"
            )
            page = context.new_page()
        else:
            page = browser.new_page()

        # Load Bing homepage and add cookies if exists
        if os.path.exists(_cookies):
            page.context.add_cookies(cookies)
        page.goto("https://www.bing.com/")

        page.wait_for_load_state("load")

        # Check login status
        # If not logged in, wait for manual login
        # If logged in, set headless mode status
        try_to_login = True # Try login to fix cookies issue
        while True and not bypass:
            print("请不要操作页面, 等待检查完成...")
            page.wait_for_timeout(5000)
            if do_phone:
                # For Phone Stimulator, click the hamburger menu and check the login status, wait for 5 seconds for each action to ensure the page is loaded
                page.wait_for_timeout(5000)
                page.evaluate("document.getElementById('mHamburger').click()")
                page.wait_for_timeout(5000)
                page.evaluate(
                    "document.getElementById('HBright').style = 'display: block;'")
                try:
                    d = page.evaluate(
                        "() => { return document.getElementById('hb_n').innerText; }")
                except:
                    d = ""
            else:
                try:
                    d = page.evaluate(
                        "() => { return document.querySelector('a#id_l').innerText; }")
                except:
                    d = ""
            print(f"检测到登录状态: {d}")
            if d == "Sign in" or d == "登录" or d == "登入" or d == "":
                if not try_to_login:
                    print("未检测到登录状态, 请手动登录...")
                    if headless:
                        print("请注意, 无头模式下无法手动登录, 将停止程序...")
                        with open(_headless, "w", encoding="utf8") as f:
                            f.write("0")
                        return False
                    input("[需要操作]登录完成后按回车键继续...")
                else:
                    print("未检测到登录状态, 正在尝试登录...")
                    if do_phone:
                        print("请不要操作页面, 等待登录完成...")
                        #make sure the hamburger menu is open
                        page.evaluate("document.getElementById('mHamburger').click()")
                        page.wait_for_timeout(5000)
                        page.evaluate(
                            "document.getElementById('HBright').style = 'display: block;'")
                        page.wait_for_timeout(5000)
                        #click #HBSignIn > a:nth-child(1)
                        page.evaluate("document.querySelector('#HBSignIn > a:nth-child(1)').click()")
                        page.wait_for_timeout(5000)
                        page.wait_for_load_state("domcontentloaded")
                    else:
                        page.click("a#id_l")
                        #click #b_idProviders > li:nth-child(1) > a
                        page.click("#b_idProviders > li:nth-child(1) > a")
                        page.wait_for_load_state("domcontentloaded")
                    # make sure the page is https://*.bing.com
                    while not re.match(r"https://.*\.bing\.com", page.url):
                        print("等待登录完成...")
                        page.wait_for_load_state("domcontentloaded")
                        time.sleep(1)
                        
                    try_to_login = False
                page.goto("https://cn.bing.com/")
                page.wait_for_load_state("domcontentloaded")
            else:
                break

        if not bypass:
            print("登录状态有效, 下次将使用无头模式")
            with open(_headless, "w", encoding="utf8") as f:
                f.write("1")

            # Cache cookies for next time, for backup in case of search failure
            print("正在缓存cookies...")
            page.goto("https://www.bing.com/")
            time.sleep(3)
            cookies = page.context.cookies()
            with open(_cookies, "w", encoding="utf8") as f:
                json.dump(cookies, f)
            print("cookies缓存完成, 下次将使用无头模式")

        else:
            print("已跳过登录状态检查")

        # Do the search
        print("开始搜索...")
        url = "https://www.bing.com/search?q="
        for i in range(0, times):
            word = read_random_line('words.txt')
            print(f"正在搜索({i+1}/{times}): {word}")
            page.goto(url+word+'&PC=U316&FORM=CHROMN')
            if do_phone:
                _phone_count += 1
            else:
                _pc_count += 1
            if not i == times - 1:
                sl = get_random_sleep_time()
                for s in range(0, sl):
                    if show_countdown:
                        print(f"等待中... {sl - s:02d}秒\r", end="", flush=True)
                    time.sleep(1)

        print("搜索完成")

        # Cache cookies for next time
        print("存储cookies...")
        cookies = page.context.cookies()
        with open(_cookies, "w", encoding="utf8") as f:
            json.dump(cookies, f)
        print("cookies存储完成, 下次将使用无头模式")

        # Close the browser
        browser.close()

        return True


if __name__ == "__main__":
    args = sys.argv
    show_countdown = not ("--hide-countdown" in args or "-c" in args)
    _bypass = "--aipc" in args

    _pc = 35
    _phone = 25

    if "--auto" in args:
        fsprint("> 自动模式, 正在获取今日积分...")
        res = check_points()

        pc_left = res["pc"][1] - res["pc"][0]
        phone_left = res["mobile"][1] - res["mobile"][0]

        _pc = int(pc_left/3)
        _phone = int(phone_left/3)

        fsprint(f"PC: {_pc} 次, Mobile: {_phone} 次")
        print("=====================================")


    if ("--not_now" in args or "-n" in args):
        _wait_for_minutes = random.randint(1, 10)
        _wait_for_seconds = random.randint(0, 59)
        fsprint(f"> 将在{_wait_for_minutes}分钟{_wait_for_seconds}秒后开始")
        print("=====================================")
        time.sleep(_wait_for_minutes * 60 + _wait_for_seconds)

    if not ("--skip-generate" in args or "-g" in args):
        fsprint("> 正在生成搜索词...")
        try:
            if "--weibo" in args:
                generate_words_weibo()
            else:
                generate_words(
                    do_jieba=False
                )
        except Exception as e:
            fsprint(f"搜索词生成失败: {e}")
            exit(1)
        fsprint("搜索词生成完成")
        print("=====================================")

    fsprint("> 开始搜索...")

    while _pc+_phone > 0:

        print(f"| 已搜索次数: PC: {_pc_count}, Mobile: {_phone_count}")
        print(f"| 剩余次数: PC: {_pc}, Mobile: {_phone}")

        _this_pc  = random.randint(2, 8)
        _this_phone = random.randint(2, 8)

        if _this_pc > _pc:
            _this_pc = _pc
        if _this_phone > _phone:
            _this_phone = _phone
        
        _pc -= _this_pc
        _phone -= _this_phone

        print(f"| 本次搜索次数: PC: {_this_pc}, Mobile: {_this_phone}")


        if not ("--skip-pc" in args or "-p" in args) and _this_pc > 0:
            print("> PC 开始搜索...")
            try:
                _p = main(_this_pc,
                        do_phone=False,
                        show_countdown=show_countdown,
                        bypass=_bypass
                        )
            except Exception as e:
                fsprint(f"PC 搜索失败: {e}")
                exit(1)
            if _p:
                print("PC 搜索完成")
            else:
                print("PC 搜索失败")

        if not ("--skip-phone" in args or "-m" in args) and _this_phone > 0:
            print("> Phone 开始搜索...")
            try:
                _p = main(_this_phone,
                        do_phone=True,
                        show_countdown=show_countdown,
                        bypass=_bypass
                        )
            except Exception as e:
                fsprint(f"Phone 搜索失败: {e}")
                exit(1)
            if _p:
                print("Phone 搜索完成")
            else:
                print("Phone 搜索失败")

        if '--auto' in args:
            print("> 检查中...")
            try:
                res = check_points()
            except Exception as e:
                fsprint(f"检查失败: {e}")
                exit(1)
            _re = ""
            _re += f"PC: {res['pc'][0]}/{res['pc'][1]} "
            _pc_diff = 0
            _mobile_diff = 0
            if res["pc"][0] == res["pc"][1]:
                _re += "OK"
            else:
                _re += "Failed, "
                _pc_diff = res["pc"][1] - res["pc"][0]
                _re += f"0{_pc_diff} left"
            _re += "\n"
            _re += f"Mobile: {res['mobile'][0]}/{res['mobile'][1]} "
            if res["mobile"][0] == res["mobile"][1]:
                _re += "OK"
            else:
                _re += "Failed, "
                _mobile_diff = res["mobile"][1] - res["mobile"][0]
                _re += f"0{_mobile_diff} left"
            print(_re)

            _pc = math.ceil(_pc_diff/3)
            _phone = math.ceil(_mobile_diff/3)
            
            print(f"| 剩余次数: PC: {_pc}, Mobile: {_phone}")
            print("=====================================")


    if not ("--skip-check" in args or "-k" in args):
        print("> 检查中...")
        try:
            res = check_points()
        except Exception as e:
            fsprint(f"检查失败: {e}")
            exit(1)
        _re = ""
        _re += f"PC: {res['pc'][0]}/{res['pc'][1]} "
        if res["pc"][0] == res["pc"][1]:
            _re += "OK"
        else:
            _re += "Failed"
        _re += "\n"
        _re += f"Mobile: {res['mobile'][0]}/{res['mobile'][1]} "
        if res["mobile"][0] == res["mobile"][1]:
            _re += "OK"
        else:
            _re += "Failed"
        fsprint(_re)

        print("=====================================")

    if not ("--skip-extra" in args or "-e" in args):
        fsprint("> 获取额外积分中...")
        try:
            p = get_extra_points()
        except Exception as e:
            fsprint(f"获取额外积分失败: {e}")
            exit(1)
        fsprint(f"获取额外积分完成, 共 {p} 分")
