from playwright.sync_api import sync_playwright
import os
import sys
import json
import typing


def main() -> typing.Dict[str, typing.List[int]]:
    """
    Check the current points of the Bing account.

    This function will check the current points of the Bing account by requesting the Bing Rewards page and parsing the JSON data.

    It requires the `cookies.json` and `.headless` files to be present in the current directory, which are generated by `bing_bot.py`.

    For the first time, it will also generate a `cookies_check.json` file and require manual confirmation to continue, then it will generate a `.headless_check` file to indicate that the check has been done.

    Returns:
        dict: A dictionary containing the points of PC search, mobile search, daily activities, and daily points. Which looks like this:
        {
            "pc": [current_points, max_points],
            "mobile": [current_points, max_points],
            "activity": [current_points, max_points],
            "daily": [current_points, max_points]
        }
    
    Raises:
        TypeError: If the browser failed to load or the page failed to load, or the cookies failed.
    """

    if not (os.path.exists('.headless') and os.path.exists('cookies.json')):
        print("请先运行bing_bot.py, 并确保cookies.json和.headless文件存在")
        sys.exit(1)

    with open('.headless', "r", encoding="utf8") as f:
        _headless = bool(int(f.read()))
    
    if not _headless:
        print("请先运行bing_bot.py, 并确保登录有效")
        sys.exit(1)
    
    if os.path.exists('.headless_check'):
        with open('.headless_check', "r", encoding="utf8") as f:
            headless = bool(int(f.read()))
    else:
        headless = False

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless
        )
        page = browser.new_page()

        if not os.path.exists('cookies_check.json'):

            with open('cookies.json', "r", encoding="utf8") as f:
                cookies = json.load(f)
            page.context.add_cookies(cookies)

            page.goto("https://www.bing.com")
            page.wait_for_load_state("load")

            with open('cookies.json', "w", encoding="utf8") as f:
                json.dump(page.context.cookies(), f)

            page.goto("https://rewards.bing.com/")
            page.wait_for_load_state("load")

            input("[需要操作]请等待自动登录完成后输入回车继续...")

            with open('cookies_check.json', "w", encoding="utf8") as f:
                json.dump(page.context.cookies(), f)

        else:
            with open('cookies_check.json', "r", encoding="utf8") as f:
                cookies = json.load(f)
            page.context.add_cookies(cookies)

        #request https://rewards.bing.com/api/getuserinfo?type=1&X-Requested-With=XMLHttpRequest
        page.goto("https://rewards.bing.com/api/getuserinfo?type=1&X-Requested-With=XMLHttpRequest")
        page.wait_for_load_state("load")

        _data = json.loads(page.evaluate("() => { return document.querySelector('pre').innerText; }"))

        with open('.headless_check', "w", encoding="utf8") as f:
            f.write("1")

        counters = _data['dashboard']['userStatus']['counters']
        
        pc_points = counters['pcSearch'][0]['pointProgress']
        pc_max_points = counters['pcSearch'][0]['pointProgressMax']
        mobile_points = counters['mobileSearch'][0]['pointProgress']
        mobile_max_points = counters['mobileSearch'][0]['pointProgressMax']
        active_points = counters['activityAndQuiz'][0]['pointProgress']
        active_max_points = counters['activityAndQuiz'][0]['pointProgressMax']
        daily_points = counters['dailyPoint'][0]['pointProgress']
        daily_max_points = counters['dailyPoint'][0]['pointProgressMax']

        return {
            "pc": [pc_points, pc_max_points],
            "mobile": [mobile_points, mobile_max_points],
            "activity": [active_points, active_max_points],
            "daily": [daily_points, daily_max_points]
        }

if __name__ == "__main__":
    print(main())