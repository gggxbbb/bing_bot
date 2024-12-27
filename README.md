# bing_bot

一个用于污染必应搜索历史的小脚本

## 依赖项

- Python 3.12+ (或许可以在更早的版本上运行)
- requests
- playwright
- jieba

## 使用方法

```shell
# 安装依赖
pip install jieba requests playwright
playwright install chromium

# 首次运行
python dump_cookies.py

# 每次运行
python bing_bot.py

# 建议使用
python bing_bot.py --auto

```

**注意**: 生成/检查手机 cookies 时会存在多次等待, 请不要在等待期间操作网页.

**仅在输出显示 [需要操作] 时操作网页, 否则可能导致脚本运行异常.**

### 参数

```shell
python bing_bot.py [-n|--not_now] [-g|--skip-generate] [-p|--skip-pc] [-m|--skip-mobile] [-e|--skip-extra] [-k|--skip-check] [-c|--hide-countdown] [--aipc] [--auto]
```

- `-n` 或 `--not_now`：让脚本在等待随机时间后再开始运行(1分钟~10分59秒), 用于 cron 等自动化任务
- `-g` 或 `--skip-generate`：跳过搜索词生成(不建议)
- `-p` 或 `--skip-pc`：跳过 PC 端搜索
- `-m` 或 `--skip-mobile`：跳过移动端搜索
- `-k` 或 `--skip-check`：跳过检查搜索结果
- `-e` 或 `--skip-extra`：跳过额外点数的获取
- `-c` 或 `--hide-countdown`：隐藏倒计时, 用于 cron 等自动化任务

- `--aipc`：跳过登录检查并始终使用无头模式
- `--auto`：自动运行, 根据已有点数计算搜索次数

当跳过生成搜索词时, 请确保 `bing_bot.py` 同目录下有 `words.txt` 文件, 且其中每行为一个搜索词. 亦可以自行编写搜索词并保存到 `words.txt` 中.

### 其他用法

可通过复制 `cookies*.json` 和 `.headless*` 文件到其他设备上, 以跳过首次运行 `generate_cookie.py` 的步骤.

可手动创建 `.feishu` 文件, 以在脚本运行时发送相关消息到飞书群组. 文件内容为飞书群组的 webhook 地址.

推送的消息参考如下:

```
将在x分钟x秒后开始
Bot 开始
正在生成搜索词...
搜索词生成完成
PC 开始搜索...
PC搜索完成(失败)
Phone 开始搜索...
Phone 搜索完成(失败)
检查中...
PC ?/? OK(Failed)
Monile ?/? OK(Failed)
额外点数获取中...
额外点数获取完成, 共?分
```

## 目录结构

```
- ms_bot
  - .feishu               # 飞书群组 webhook 地址
  - .headless             # PC 端无头模式配置
  - .headless_check       # PC 端无头模式配置(用于检查)
  - .headless_mobile      # 移动端无头模式配置
  - cookies.json          # 用于 PC 端的 cookies
  - cookies_check.json    # 用于检查的 cookies
  - cookies_phone.json    # 用于移动端的 cookies
  - dump_cookies.py       # 用于生成 cookies 的脚本
  - generate_words.py     # 生成搜索词
  - bing_bot.py           # 主脚本
  - words.txt             # 搜索词文件
  - README.md             # 本文件
```

`.headless`,`.headless_check`,`.headless_mobile` 由脚本生成. 当其内容为 `1` 时, 表示启用无头模式; 为 `0` 时, 表示启用有头模式.

`cookies.json`, `cookies_check.json`, `cookies_phone.json` 由脚本生成. 用于保存 cookies 信息.

`.feishu` 用于保存飞书群组的 webhook 地址, 非必需.