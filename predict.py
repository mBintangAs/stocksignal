from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange
from news import get_news
from telegram import send_telegram_message
import yfinance as yf
import pandas as pd
from flask import  jsonify
import requests

api_url = "http://127.0.0.1:8000/api/signal"  # Ganti dengan URL API tujuan

# Fungsi untuk hitung indikator teknikal
def calculate_indicators(df):
    # df['date']= df[0]
    df["ma20"] = SMAIndicator(close=df["Close"], window=20).sma_indicator()
    df["ma50"] = SMAIndicator(close=df["Close"], window=50).sma_indicator()

    df["rsi_14"] = RSIIndicator(close=df["Close"], window=14).rsi()

    macd = MACD(close=df["Close"])
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    atr = AverageTrueRange(high=df["High"], low=df["Low"], close=df["Close"])
    df["atr"] = atr.average_true_range()

    df["vol_avg5"] = df["Volume"].rolling(window=5).mean()
    return df

def post_api(url, data):
    """
    Endpoint untuk mengirimkan sinyal trading ke API eksternal
    """
    try:
        response = requests.post(url, json=data)
        if response.status_code != 200:
            raise ValueError(f"Error {response.status_code}: {response.text}")
        
        print(f"Data sent successfully to {url}")

    except Exception as e:
        with open("log.txt", "a") as f:
            f.write(f"Error send to api: {e}\n")

def get_signal_logic():
    """
    Endpoint untuk mendapatkan sinyal trading
    """
    # Daftar ticker IDX (bisa lebih banyak)
    tickers_df = pd.read_csv('./tickers.csv', header=0)
    tickers = tickers_df['Code'].astype(str).tolist()
    ticker_to_name = dict(zip(tickers_df['Code'], tickers_df['Company Name']))

    # Parameter strategi
    # PERSENTASE CUT LOSS DAN TAKE PROFIT
    cut_loss_pct = 0.03
    take_profit_pct = 0.05

    results = []

    # Loop per ticker
    for ticker in tickers:
        try:
            # Download data untuk ticker
            df = yf.download(tickers=ticker+".JK", period="3mo", interval="1d",progress=False, auto_adjust=False,multi_level_index=False)
            df.columns.name = None
            print(f"Processing {ticker}...")
            # Validasi panjang data
            if len(df) < 50:
                continue

            # Hitung indikator
            df = calculate_indicators(df).dropna()


            # Ambil bar terakhir dan sebelumnya
            latest = df.iloc[-1]
            prev = df.iloc[-2]

            # Skoring strategi
            score = 0
            reasons = []
            if latest["Close"] > latest["ma20"] and latest["Close"] > latest["ma50"]:
                score += 1
                reasons.append("Close > MA20 & Close > MA50")
            if latest["macd"] > latest["macd_signal"] and prev["macd"] <= prev["macd_signal"]:
                score += 1
                reasons.append("MACD bullish crossover")
            if latest["rsi_14"] < 35 and latest['rsi_14'] > prev['rsi_14']:
                score += 1
                reasons.append("RSI 14 < 35 AND RSI Today > RSI Yesterday")
            if latest["Volume"] > latest["vol_avg5"]:
                score += 1
                reasons.append("Volume > 5-day average")
            if latest["atr"] > df["atr"].mean():
                score += 1
                reasons.append("ATR above average")

            date = latest.name.strftime('%d-%m-%Y')

            # Tambahkan jika layak
            if score > 0:
                entry = round(latest["Close"], 2)
                cutloss = round(entry * (1 - cut_loss_pct), 2)
                target = round(entry * (1 + take_profit_pct), 2)
                results.append({
                    "ticker": ticker.replace(".JK", ""),
                    "date": date,
                    "close_price":latest['Close'],
                    "open_price":latest['Open'],
                    "entry_price": entry,
                    "cut_loss": cutloss,
                    "target_price": target,
                    "score": score,
                    "reasons": reasons,
                })

        except Exception as e:
            print(f"Gagal memproses {ticker}: {e}")
            continue

    # Ambil top 3 saham berdasarkan skor tertinggi
    top_3 = sorted(results, key=lambda x: x["score"], reverse=True)[:3]

    # Loop dan tambahkan berita ke setiap objek top_3
    for saham in top_3:
        company_name = saham.get('company_name', '')
        print(f"Fetching news for {company_name} ({saham['ticker']})")
        news = get_news(company_name+"+"+ saham['ticker'])
        saham['news'] = news  # Tambahkan list berita ke objek saham
    # Kirim data ke API eksternal
    post_api(api_url, {"signal": top_3})
    for message in top_3:
        send_telegram_message(message)
    # Kembalikan hasil sebagai JSON

