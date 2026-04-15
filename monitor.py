import requests
import os
from datetime import datetime, timedelta

PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN")
HISTORY = {}

def beijing_now():
    return datetime.utcnow() + timedelta(hours=8)

def get_price():
    try:
        url = "https://api.jdjygold.com/gw2/generic/jrm/h5/m/stdLatestPrice?productSku=1961543816"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        return round(float(r.json()["resultData"]["datas"]["price"]), 2)
    except:
        return None

def send(title, content):
    if not PUSHPLUS_TOKEN:
        return
    try:
        requests.post("https://www.pushplus.plus/send", 
                      json={"token": PUSHPLUS_TOKEN, "title": title, "content": content}, 
                      timeout=8)
    except:
        pass

def main():
    now = beijing_now()
    today = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M")
    price = get_price()

    if not price:
        return

    global HISTORY
    day_history = HISTORY.get(today, [])

    # 8点基准价
    if not day_history and "08:00" <= time_str <= "09:30":
        day_history = [(time_str, price)]
        send("🌅 {time_str}点金价", f"价格：{price} 元/克")

    # 波动推送
    elif day_history:
        last_p = day_history[-1][1]
        if abs(price - last_p) >= 5:
            day_history.append((time_str, price))
            send("📈 金价波动≥5元", f"最新：{price} 元/克")

    HISTORY[today] = day_history

if __name__ == "__main__":
    main()
