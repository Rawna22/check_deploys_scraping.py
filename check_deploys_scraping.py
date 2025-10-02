import os, time, random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

WALLET = os.getenv("WALLET", "0x2e5392f3d727a5c0e5a2e4a3530c2254dbce205d")

# ===== Optional API (lebih akurat & tahan anti-bot) =====
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")      # isi kalau punya
BASESCAN_API_KEY   = os.getenv("BASESCAN_API_KEY")      # isi kalau punya

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36",
]
HEADERS = {"User-Agent": random.choice(UA_LIST), "Accept-Language": "en-US,en;q=0.8"}

def human_dt(ts):
    try:
        return datetime.fromtimestamp(int(ts)).isoformat(sep=" ", timespec="seconds")
    except:
        return ts

def via_api():
    results = []
    endpoints = [
        ("Ethereum Mainnet", f"https://api.etherscan.io/api?module=account&action=txlist&address={WALLET}&startblock=0&endblock=99999999&sort=asc&apikey={ETHERSCAN_API_KEY}"),
        ("Base Mainnet",     f"https://api.basescan.org/api?module=account&action=txlist&address={WALLET}&startblock=0&endblock=99999999&sort=asc&apikey={BASESCAN_API_KEY}"),
        ("Base Sepolia",     f"https://api-sepolia.basescan.org/api?module=account&action=txlist&address={WALLET}&startblock=0&endblock=99999999&sort=asc&apikey={BASESCAN_API_KEY}"),
    ]
    for chain, url in endpoints:
        if ("etherscan" in url and not ETHERSCAN_API_KEY) or ("basescan" in url and not BASESCAN_API_KEY):
            continue
        try:
            r = requests.get(url, timeout=30)
            data = r.json()
            if data.get("status") != "1":
                continue
            for tx in data["result"]:
                if tx.get("to") in ("", "0x0000000000000000000000000000000000000000"):
                    results.append({
                        "Chain": chain,
                        "Tx Hash": tx["hash"],
                        "Block": tx["blockNumber"],
                        "Date": human_dt(tx["timeStamp"]),
                        "From": tx["from"],
                        "Contract Address": tx.get("contractAddress", "N/A"),
                        "Method": "Contract Creation"
                    })
        except Exception as e:
            pass
        time.sleep(0.5)
    return results

def scrape_chain(chain_name, base_url):
    """Paginate ?ps=100&page=1..N dan cari baris 'Contract Creation'."""
    out = []
    session = requests.Session()
    page = 1
    while True:
        url = f"{base_url}&ps=100&p={page}"
        try:
            resp = session.get(url, headers=HEADERS, timeout=30)
            if resp.status_code != 200:
                # ganti UA + retry kecil
                HEADERS["User-Agent"] = random.choice(UA_LIST)
                time.sleep(1.2)
                resp = session.get(url, headers=HEADERS, timeout=30)
            if resp.status_code != 200:
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            rows = soup.select("table tbody tr")
            if not rows:
                break

            found_on_page = 0
            for row in rows:
                tds = row.find_all("td")
                if len(tds) < 7: 
                    continue
                # kolom biasanya: Txn Hash | Age | From | To/Method | ...
                # cara lebih aman: cek text 'Contract Creation' pada row
                row_text = row.get_text(" ").strip()
                if "Contract Creation" in row_text:
                    link = row.select_one("a[href*='/tx/']")
                    tx_hash = link.text.strip() if link else "N/A"
                    # ambil tanggal/age di kolom ke-2
                    age = tds[1].get_text(strip=True)
                    out.append({
                        "Chain": chain_name,
                        "Tx Hash": tx_hash,
                        "Age / Date": age,
                        "Method": "Contract Creation",
                        "To": "Contract Creation"
                    })
                    found_on_page += 1
            # lanjut halaman berikutnya; hentikan bila halaman tidak menambah hasil
            page += 1
            # batasi max 10 halaman supaya aman
            if page > 10: 
                break
            # jeda kecil agar tidak ditandai bot
            time.sleep(1.0 + random.random()*0.5)
            # jika page tidak berisi apapun, stop
            if found_on_page == 0 and len(rows) < 100:
                break
        except Exception:
            break
    return out

def main():
    deploys = []

    # 1) Coba API jika key tersedia
    api_deploys = via_api()
    deploys.extend(api_deploys)

    # 2) Scrape sebagai fallback / tambahan
    urls = {
        "Ethereum Mainnet": f"https://etherscan.io/txs?a={WALLET}",
        "Base Mainnet":     f"https://basescan.org/txs?a={WALLET}",
        "Base Sepolia":     f"https://sepolia.basescan.org/txs?a={WALLET}"
    }
    for chain, base_url in urls.items():
        # skip scrape etherscan kalau sudah tercover API (opsional)
        if chain == "Ethereum Mainnet" and ETHERSCAN_API_KEY:
            continue
        if chain.startswith("Base") and BASESCAN_API_KEY:
            continue
        deploys.extend(scrape_chain(chain, base_url))

    df = pd.DataFrame(deploys).drop_duplicates(subset=["Tx Hash", "Chain"])
    if df.empty:
        print("\nTidak ditemukan transaksi Contract Creation untuk wallet:", WALLET)
    else:
        print("\n📊 Hasil Contract Deploy:")
        print(df.to_string(index=False))

    df.to_csv("contract_deploys_scraped.csv", index=False)
    print("\nHasil disimpan ke contract_deploys_scraped.csv")

if __name__ == "__main__":
    main()