# 🛠️ Contract Deploy Checker

Cek berapa kali sebuah wallet sudah melakukan **smart contract deployment (Contract Creation)** di:
- Ethereum Mainnet
- Base Mainnet
- Base Sepolia Testnet

Dibuat dengan Python, bisa dijalankan langsung di **GitHub Codespaces**.

---

## ⚡ Cara Pakai (GitHub Codespaces)

1. **Buat Repo Baru**
   - Login ke GitHub → klik **New Repository**
   - Nama: `check-contract-deploys`
   - Centang `Add a README` → Create repo

2. **Buka di Codespaces**
   - Masuk ke repo → klik tombol hijau **Code**
   - Pilih tab **Codespaces** → klik **Create codespace on main**

3. **Buat File Script**
   - Buat file `check_deploys_scraping.py`
   - Copy–paste isi script dari repo ini

4. **Install Dependensi**
   ```bash
   pip install requests beautifulsoup4 pandas
   ```
5. **Jalankan Script**
   ```bash
   python check_deploys_scraping.py
   ```
6. **Hasil**
   - Akan tampil di terminal tabel transaksi Contract Creation
   - Data juga otomatis tersimpan ke file contract_deploys_scraped.csv
