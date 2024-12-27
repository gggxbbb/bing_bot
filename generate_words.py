from playwright.sync_api import sync_playwright
import jieba
import re
import requests
import datetime
import re


def main(do_jieba=True):
    """
    A function to generate words from a website.

    This function will generate words from ITHome website and write them to a file named `words.txt`.

    The way it generates words is by getting all the text from the website, then split the text into words using jieba, then combine the words into 4-grams and write them to the file.
    """

    source_list = [
        "http://www.xinhuanet.com/",
        "http://www.people.com.cn/",
        "http://www.cctv.com/",
        "http://www.cri.cn/",
        "http://www.ithome.com/",
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        words = []

        for source in source_list:
            page.goto(source)
            words += page.evaluate(
                "() => { return Array.from(document.querySelectorAll('a')).map(a => a.innerText).filter(a => a.length > 1); }")

        words_list = []

        if do_jieba:
            for word in words:

                _w = jieba.lcut(word)

                # 移除_w中长度小于3的词
                _w = [w for w in _w if len(w) >= 3]

                for i in range(0, len(_w)):
                    for j in range(0, len(_w)):
                        for k in range(0, len(_w)):
                            for l in range(0, len(_w)):
                                for m in range(0, len(_w)):
                                    if i == j or j == k or i == k or i == l or j == l or k == l or i == m or j == m or k == m or l == m:
                                        continue
                                    _s = f"{_w[i]}{_w[j]}{_w[k]}{_w[l]}{_w[m]}"
                                    words_list.append(_s)
        else:
            for word in words:
                #remove special characters
                word = re.sub(r'[^\w\s]', '', word)
                #remove \n or \t
                word = word.replace("\n", "").replace("\t", "")
                while "  " in word:
                    word = word.replace("  ", " ")
                #remove start and end space
                word = word.strip()
                words_list.append(word)

        words_list = list(set(words_list))
        # 移除words_list中长度小于20的内容
        words_list = [w for w in words_list if len(w) >= 10]
        # 移除words_list中的无中文内容
        words_list = [w for w in words_list if re.search(
            r'[\u4e00-\u9fa5]', w)]

        with open("words.txt", "w", encoding="utf8") as f:
            f.write("\n".join(words_list))



def str4(s):
    _s = str(s)
    if len(_s) == 4:
        return _s
    elif len(_s) == 3:
        return "0" + _s
    elif len(_s) == 2:
        return "00" + _s
    elif len(_s) == 1:
        return "000" + _s
    else:
        return "0000"

def str2(s):
    _s = str(s)
    if len(_s) == 2:
        return _s
    elif len(_s) == 1:
        return "0" + _s
    else:
        return "00"

def main2():
    _url = "https://gxb.pub/https://raw.githubusercontent.com/hotarchive/Weibo/main/archives/{2024}/{08}/{2024}-{08}-{10}.md"
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    last_2days = now - datetime.timedelta(days=2)
    last_3days = now - datetime.timedelta(days=3)
    last_4days = now - datetime.timedelta(days=4)
    last_week = now - datetime.timedelta(days=7)
    last2_week = now - datetime.timedelta(days=14)
    last_month = now - datetime.timedelta(days=30)
    _urls = [
        _url.replace("{2024}", str4(now.year)).replace("{08}", str2(now.month)).replace("{10}", str2(now.day)),
        _url.replace("{2024}", str4(yesterday.year)).replace("{08}", str2(yesterday.month)).replace("{10}", str2(yesterday.day)),
        _url.replace("{2024}", str4(last_2days.year)).replace("{08}", str2(last_2days.month)).replace("{10}", str2(last_2days.day)),
        _url.replace("{2024}", str4(last_3days.year)).replace("{08}", str2(last_3days.month)).replace("{10}", str2(last_3days.day)),
        _url.replace("{2024}", str4(last_4days.year)).replace("{08}", str2(last_4days.month)).replace("{10}", str2(last_4days.day)),
        _url.replace("{2024}", str4(last_week.year)).replace("{08}", str2(last_week.month)).replace("{10}", str2(last_week.day)),
        _url.replace("{2024}", str4(last2_week.year)).replace("{08}", str2(last2_week.month)).replace("{10}", str2(last2_week.day)),
        _url.replace("{2024}", str4(last_month.year)).replace("{08}", str2(last_month.month)).replace("{10}", str2(last_month.day)),
    ]
    words_list = []
    for _url in _urls:
        _res = requests.get(_url)
        _res.encoding = "utf8"
        _content = _res.text
        _lines = _content.split("\n")
        for line in _lines:
            if line.startswith("1. "):
                #提取 [] 中的内容
                _words = re.findall(r'\[(.*?)\]', line)
                words_list += _words
    words_list = list(set(words_list))
    with open("words.txt", "w", encoding="utf8") as f:
        f.write("\n".join(words_list))

if __name__ == "__main__":
    main(do_jieba=False)
