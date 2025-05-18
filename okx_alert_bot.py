import requests
import datetime

# Telegram 資訊
BOT_TOKEN = "8115235500:AAHY_6nNaphuuJasz4F7esWOJdwUK-p_JOk"
CHAT_ID = "-1002617752512"

# 取得 OKX 所有 USDT 現貨交易對
def get_okx_symbols():
    url = "https://www.okx.com/api/v5/public/instruments?instType=SPOT"
    r = requests.get(url)
    data = r.json()["data"]
    return [item["instId"] for item in data if item["quoteCcy"] == "USDT"]

# 取得日K線資料（取得最近3根K線）
def get_okx_ohlcv(symbol):
    url = f"https://www.okx.com/api/v5/market/candles?instId={symbol}&bar=1D&limit=3"
    r = requests.get(url)
    return r.json()["data"]

# 檢查是否為連續兩根陽線，並回傳最近一根的成交量
def check_two_bullish_and_volume(kline_data):
    try:
        last2 = kline_data[:2]
        if all(float(k[4]) > float(k[1]) for k in last2):
            volume = float(last2[0][5])  # 最近一根K線的成交量（成交量在第6欄）
            return True, volume
        else:
            return False, 0
    except:
        return False, 0

# 傳送訊息到 Telegram
def send_to_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=payload)

# 主流程
def main():
    symbols = get_okx_symbols()
    matched = []

    for sym in symbols:
        try:
            kline = get_okx_ohlcv(sym)
            is_bullish, volume = check_two_bullish_and_volume(kline)
            if is_bullish:
                matched.append((sym, volume))
        except:
            continue

    # 按成交量從大到小排序
    matched.sort(key=lambda x: x[1], reverse=True)
    top5 = matched[:5]

    today = datetime.datetime.now().strftime('%Y/%m/%d')
    msg = f"{today} 日線兩陽 + 高成交量排行前5\n========\n"
    for i, (sym, vol) in enumerate(top5):
        msg += f"{i+1}. {sym}（成交量: {vol:,.2f}）\n"
    msg += f"\n總符合條件交易對數量: {len(matched)}"

    send_to_telegram(msg)

main()
