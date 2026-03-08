import requests

URLS = [
    "https://api.atlasacademy.io/export/JP/nice_quest.json",
    "https://api.atlasacademy.io/export/JP/basic_quest.json",
    "https://api.atlasacademy.io/export/JP/nice_quest_latest.json",
    "https://api.atlasacademy.io/export/JP/nice_war.json" 
]

def check_urls():
    for url in URLS:
        try:
            r = requests.head(url, timeout=5)
            print(f"{url}: {r.status_code}")
        except Exception as e:
            print(f"{url}: Error {e}")

if __name__ == "__main__":
    check_urls()
