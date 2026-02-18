import requests
import time
from datetime import datetime

BINANCE_FUNDING_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
BINANCE_SPOT_URL = "https://api.binance.com/api/v3/ticker/price"
SYMBOL = "BTCUSDT"

FUNDING_ALERT_THRESHOLD = 0.0005   # 0.05%
BASIS_ALERT_THRESHOLD = 50         # USD difference


def get_funding_and_mark_price():
    try:
        response = requests.get(BINANCE_FUNDING_URL, timeout=5)
        data = response.json()

        for item in data:
            if item["symbol"] == SYMBOL:
                funding_rate = float(item["lastFundingRate"])
                mark_price = float(item["markPrice"])
                return funding_rate, mark_price

    except Exception as e:
        print("Funding API Error:", e)

    return None, None


def get_spot_price():
    try:
        response = requests.get(BINANCE_SPOT_URL, params={"symbol": SYMBOL}, timeout=5)
        data = response.json()
        return float(data["price"])

    except Exception as e:
        print("Spot API Error:", e)

    return None


def check_alerts(funding_rate, basis):
    alerts = []

    if abs(funding_rate) > FUNDING_ALERT_THRESHOLD:
        alerts.append(f"⚠ Funding Rate Alert: {funding_rate:.6f}")

    if abs(basis) > BASIS_ALERT_THRESHOLD:
        alerts.append(f"⚠ Basis Alert: {basis:.2f} USD")

    return alerts


def main():
    print("Starting Funding & Basis Monitor...\n")

    while True:
        funding_rate, mark_price = get_funding_and_mark_price()
        spot_price = get_spot_price()

        if funding_rate is None or spot_price is None:
            print("Data retrieval failed. Retrying...\n")
            time.sleep(5)
            continue

        basis = mark_price - spot_price

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        print(f"[{timestamp} UTC]")
        print(f"Funding Rate: {funding_rate:.6f}")
        print(f"Mark Price: {mark_price:.2f}")
        print(f"Spot Price: {spot_price:.2f}")
        print(f"Basis: {basis:.2f} USD")

        alerts = check_alerts(funding_rate, basis)

        if alerts:
            print("\n".join(alerts))

        print("-" * 50)

        time.sleep(10)


if __name__ == "__main__":
    main()
