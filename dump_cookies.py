from bing_bot import main as bing_bot
from check_points import main as check_points

if __name__ == "__main__":
    print("获取 PC Cookies...")
    bing_bot(0, do_phone=False)
    print("获取 Phone Cookies...")
    bing_bot(0, do_phone=True)
    print("获取 Check Cookies...")
    check_points()