import requests
import time
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Configuration
ICECAST_URL = os.getenv('ICECAST_URL', 'http://icecast:8000/status-json.xsl')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', '5'))
MOUNT_POINT = os.getenv('MOUNT_POINT', '/cantaguarico')

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID or "YOUR_" in TELEGRAM_BOT_TOKEN:
        logging.warning("Telegram credentials not set or invalid. Skipping alert.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        logging.info("Telegram alert sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send Telegram alert: {e}")

def check_source_status():
    try:
        response = requests.get(ICECAST_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # Icecast JSON structure can vary. 'source' can be a dict (one source) or list (multiple).
        # Or it might not exist if no sources are connected.
        icestats = data.get('icestats', {})
        sources = icestats.get('source', [])
        
        if isinstance(sources, dict):
            sources = [sources]
            
        if not sources:
            return False

        for source in sources:
            # Check if listenurl ends with our mount point or if 'mount' key matches
            # Some icecast versions use 'mount' key in JSON, others imply it via listenurl
            listen_url = source.get('listenurl', '')
            mount = source.get('mount', '')
            
            if listen_url.endswith(MOUNT_POINT) or mount == MOUNT_POINT:
                return True
        
        return False
    except Exception as e:
        logging.error(f"Error checking Icecast status: {e}")
        return False

def main():
    logging.info(f"Starting Source Monitor for {MOUNT_POINT}...")
    logging.info(f"Check Interval: {CHECK_INTERVAL}s")
    
    # Initial state assumption: We don't know. 
    # We'll do a first check and set the state.
    # If it's down initially, we might want to alert or just wait for it to come up.
    # Let's assume we only alert on CHANGES.
    
    last_status = check_source_status()
    status_text = "ONLINE" if last_status else "OFFLINE"
    logging.info(f"Initial Status: {status_text}")
    
    send_telegram_alert(f"🤖 **Guardian Bot Iniciado**\nEstado actual: {status_text}")
    
    while True:
        time.sleep(CHECK_INTERVAL)
        current_status = check_source_status()
        
        if last_status != current_status:
            if current_status:
                logging.info("✅ Source CONNECTED")
                send_telegram_alert(f"🟢 **RADIO ONLINE**: La fuente {MOUNT_POINT} se ha conectado.")
            else:
                logging.info("❌ Source DISCONNECTED")
                send_telegram_alert(f"🔴 **RADIO OFFLINE**: La fuente {MOUNT_POINT} se ha desconectado.")
            
            last_status = current_status

if __name__ == "__main__":
    main()
