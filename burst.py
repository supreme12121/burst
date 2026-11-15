import os
import time
import random
import urllib.request
import urllib.error
import json

# ==========================================
# CONFIGURATION - HARDCODE THESE
# ==========================================
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = "1568575681045078148"
TARGET_USER_ID = "1478780956172357807"
WORDLIST_FILE = "pressing.txt"

# ==========================================
# SENDER LOGIC
# ==========================================
def main():
    if not TOKEN:
        print("Error: TOKEN not found in environment variables.")
        return

    if not os.path.exists(WORDLIST_FILE):
        print(f"Error: {WORDLIST_FILE} not found in the current directory.")
        return

    # Load the wordlist
    with open(WORDLIST_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    total_lines = len(lines)
    print(f"Loaded {total_lines} lines from {WORDLIST_FILE}.")
    print(f"Targeting channel: {CHANNEL_ID}")
    print(f"Target User: <@{TARGET_USER_ID}> (30% chance to mention)")
    print("Starting in 3 seconds...")
    time.sleep(3)

    url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"

    sent_count = 0

    for i, line in enumerate(lines):
        # 30% chance to inject the mention
        if random.random() < 0.30:
            if random.choice([True, False]):
                content = f"<@{TARGET_USER_ID}> {line}"
            else:
                content = f"{line} <@{TARGET_USER_ID}>"
        else:
            content = line

        # Prepare the built-in urllib request
        data = json.dumps({"content": content}).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Authorization', TOKEN)
        req.add_header('Content-Type', 'application/json')
        req.add_header('User-Agent', 'Mozilla/5.0') # Discord requires a User-Agent

        try:
            with urllib.request.urlopen(req) as response:
                if response.status in [200, 201]:
                    sent_count += 1
                    print(f"[{sent_count}/{total_lines}] Sent: {content[:50]}...")
                
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("Rate limited! Sleeping for 10 seconds...")
                time.sleep(10)
                # Retry the same message
                try:
                    with urllib.request.urlopen(req) as retry_response:
                        if retry_response.status in [200, 201]:
                            sent_count += 1
                            print(f"[{sent_count}/{total_lines}] Retried & Sent: {content[:50]}...")
                except Exception as retry_e:
                    print(f"Retry failed: {retry_e}")
            else:
                print(f"Failed to send (HTTP {e.code})")
                
        except Exception as e:
            print(f"Network error: {e}")

        # Random delay between 1 and 6 seconds
        if i < total_lines - 1:
            delay = random.uniform(1.0, 6.0)
            time.sleep(delay)

    print("Finished sending all lines.")

if __name__ == "__main__":
    main()
