import requests

TOKEN = "8442260188:AAGSt3aSvEj-rzaMOcENu2Zal226IrDNK9Q"
CHAT_ID = "-4906781120" # Trying with negative ID based on URL

def test_telegram():
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": "🔔 Test message from Antigravity Agent",
        "parse_mode": "Markdown"
    }
    try:
        print(f"Sending to {CHAT_ID}...")
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_telegram()
