from playwright.sync_api import sync_playwright
import os
import sys
import json
import random
import time

def get_extra_points(debug: bool = False) -> int:
    """
    Get extra points from Bing.

    Args:
        debug (bool, optional): Whether to run the browser in debug mode. Defaults to False. If set to True, the browser will be run in non-headless mode.
    
    Returns:
        int: The total points earned.
    """

    #check if .headless and cookies.json exist
    if not (os.path.exists('.headless') and os.path.exists('cookies.json')):
        print("请先运行bing_bot.py, 并确保cookies.json和.headless文件存在")
        sys.exit(1)
    
    #check if login is successful
    with open('.headless', "r", encoding="utf8") as f:
        _headless = bool(int(f.read()))

    if not _headless:
        print("请先运行bing_bot.py, 并确保登录有效")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=_headless and not debug
        )
        page = browser.new_page()


        with open('cookies.json', "r", encoding="utf8") as f:
            cookies = json.load(f)
        page.context.add_cookies(cookies)

        page.goto("https://www.bing.com")
        page.wait_for_load_state("load")

        #update cookies.json
        with open('cookies.json', "w", encoding="utf8") as f:
            json.dump(page.context.cookies(), f)
        
        #goto https://cn.bing.com/rewards/panelflyout
        page.goto("https://cn.bing.com/rewards/panelflyout")
        page.wait_for_load_state("load")

        #get all the divs with class "promo_cont"
        divs = page.query_selector_all(".promo_cont")

        p=0

        for div in divs:
            #check if the div contains svg with class "rw-si add"
            if div.query_selector(".rw-si.add"):
                #get title from p.promo-title
                title = div.query_selector("p.promo-title").inner_text()
                #get points from div.shortPoint
                points = div.query_selector(".shortPoint").inner_text()

                #print title and points
                print(f"{title}: {points}")

                p += int(points)

                #click the div
                div.click()
                time.sleep(random.randint(1, 3))
        
        print(f"总共获得{p}积分")
        return p
            

if __name__ == "__main__":
    get_extra_points()