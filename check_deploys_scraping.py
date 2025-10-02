import requests
import pandas as pd
from bs4 import BeautifulSoup

WALLET = "0x2e5392f3d727a5c0e5a2e4a3530c2254dbce205d"

# Explorer URL untuk normal transactions
URLS = {
    "Ethereum Mainnet": f"https://etherscan.io/txs?a={WALLET}",
    "Base Mainnet": f"https://basescan.org/txs?a={WALLET}",
    "Base Sepolia Testnet": f"https://sepolia.basescan.org/txs?a={WALLET}"
}

deploys = []

for chain, url in URLS.items():
    print(f"[{chain}] Cek {url} ...")
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Gagal akses {chain}")
        continue
    
    soup = BeautifulSoup(resp.text, "html.parser")
    rows = soup.select("table tbody tr")
    
    for row in rows:
        cols = [c.text.strip() for c in row.select("td")]
        if len(cols) < 7:
            continue

        tx_hash = row.select_one("td a").text.strip()
        method = cols[2]
        to_addr = cols[5]
        
        # Tanda contract creation
        if "Contract Creation" in method or "Contract Creation" in to_addr:
            deploys.append({
                "Chain": chain,
                "Tx Hash": tx_hash,
                "Age / Date": cols[1],
                "Method": method,
                "To": to_addr
            })

# Buat dataframe
df = pd.DataFrame(deploys)
print("\n📊 Hasil Contract Deploy:")
print(df)

# Simpan ke CSV
df.to_csv("contract_deploys_scraped.csv", index=False)
print("\nHasil disimpan ke contract_deploys_scraped.csv")
