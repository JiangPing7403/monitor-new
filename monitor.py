import requests
import json
import os
from datetime import datetime, timedelta

# 配置
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN")
PRICE_CHANGE_THRESHOLD = 5
HISTORY_FILE = "/tmp/gold_history.json"

# 北京时间
def beijing_now():
    return datetime.utcnow() + timedelta(hours=8)

# 获取浙商黄金价格
def get_price():
    url = "https://api.jdjygold.com/gw2/generic/jrm/h5/m/stdLatestPrice?productSku=1961543816"
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://m.jdjygold.com/"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return round(float(res.json()["resultData"]["datas"]["price"]), 2)
    except:
        return None

# 微信推送
def send_wechat(title, content):
    if not PUSHPLUS_TOKEN:
        return
    requests.post("https://www.pushplus.plus/send", json={
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": content
    }, timeout=8)

# 历史记录
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_history(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

# 主逻辑
def main():
    now = beijing_now()
    today = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M")
    price = get_price()

    if not price:
        return

    hist = load_history()
    day = hist.get(today, [])

    # 8:00~8:02 推送基准价
    if not day and "22:01" <= time <= "22:12":
        day = [(time, price)]
        send_wechat("🌅 {time} 浙商黄金基准价", f"价格：{price} 元/克")

    # 波动≥5元推送
    elif day:
        last_t, last_p = day[-1]
        if abs(price - last_p) >= 5:
            day.append((time, price))
            msg = "【今日金价记录】\n"
            for i, (t, p) in enumerate(day, 1):
                msg += f"价格{i}：{p} 元/克（{t}）\n"
            send_wechat("📈 金价波动≥5元", msg.strip())

    hist[today] = day
    save_history(hist)

if __name__ == "__main__":
    main()
