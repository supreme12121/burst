import os
import time
import random
import requests

# ==========================================
# CONFIGURATION - HARDCODE THESE
# ==========================================
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = "1568575681045078148" # <--- HARDCODE YOUR CHANNEL ID HERE
TARGET_USER_ID = "1478780956172357807" # <--- HARDCODE THE TARGET'S USER ID HERE
WORDLIST_FILE = "pressing.txt" # <--- YOUR WORDLIST FILE NAME

# ==========================================
# SENDER LOGIC
# ==========================================
def main():
    if not TOKEN:
        print("Error: TOKEN not found in .env file.")
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
    headers = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }

    sent_count = 0

    for i, line in enumerate(lines):
        # 30% chance to inject the mention
        if random.random() < 0.30:
            # 50/50 chance to put the mention at the start or end
            if random.choice([True, False]):
                content = f"<@{TARGET_USER_ID}> {line}"
            else:
                content = f"{line} <@{TARGET_USER_ID}>"
        else:
            content = line

        payload = {"content": content}

        try:
            response = requests.post(url, headers=headers, json=payload)
            
            # Handle Rate Limiting (429)
            if response.status_code == 429:
                print(f"Rate limited! Sleeping for 10 seconds...")
                time.sleep(10)
                # Retry the same message after sleeping
                response = requests.post(url, headers=headers, json=payload)

            if response.status_code in [200, 201]:
                sent_count += 1
                print(f"[{sent_count}/{total_lines}] Sent: {content[:50]}...")
            else:
                print(f"Failed to send (HTTP {response.status_code}): {response.text}")

        except Exception as e:
            print(f"Network error: {e}")

        # Random delay between 1 and 6 seconds
        if i < total_lines - 1:
            delay = random.uniform(1.0, 6.0)
            time.sleep(delay)

    print("Finished sending all lines.")

if __name__ == "__main__":
    main()
