# DreconisR

**DreconisR** adalah CLI tool ringan untuk mencari direktori tersembunyi di sebuah situs. Dirancang agar proses scanning lebih stabil, bersih, dan bisa dipakai langsung tanpa konfigurasi rumit.

---

## 🔧 Instalasi

```bash
git clone https://github.com/G181124/DreconisR
cd DreconisR
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Cara Pakai Singkat

```bash
python3 dreconisr.py -u <target_url> [pilih salah satu wordlist] [opsi tambahan]
```

Contoh:
```bash
python3 dreconisr.py -u https://example.com --admin --save --json
```

---

## 📂 Pilihan Wordlist

Pilih satu sesuai kebutuhan. Jika tidak memilih, tool akan menggunakan `--fpath` secara otomatis.

| Opsi         | File                  | Isi                                      |
|--------------|------------------------|-------------------------------------------|
| `--admin`    | `xdata/authpaths.txt`  | Path login/admin                          |
| `--fpath`    | `xdata/deepmap.txt`    | Path umum dan file yang sering terbuka    |
| `--fmanager` | `xdata/uplinks.txt`    | Path file manager / upload                |
| `--fullscope`| `xdata/fullscope.txt`  | Gabungan semua wordlist di atas           |

---

## ⚙️ Opsi Lain

| Opsi             | Fungsi                                                                    |
|------------------|---------------------------------------------------------------------------|
| `--save`         | Simpan hasil ke file `.txt` di folder `output/`                           |
| `--json`         | Simpan hasil juga dalam format `.json`                                    |
| `--status`       | Filter hasil berdasarkan status tertentu, contoh `--status 200,403`      |
| `--verbose`      | Tampilkan semua hasil, termasuk error                                     |
| `--threads`      | Default 10. Ideal 10–30. Maksimal 100                                     |
| `--timeout`      | Default 5 detik. Maksimum 60 detik                                        |
| `--delay`        | Delay antar request (dalam detik). Berguna untuk menghindari rate-limit  |
| `--fastscan`     | Mode cepat preset: `threads=30 timeout=2 status=200,403`                 |

---

## 🚦 Validasi Otomatis

- `--threads > 100` tidak diizinkan
- `--threads >= 50` akan memunculkan peringatan
- `--timeout > 60` tidak diizinkan
- `--timeout > 10` akan memunculkan peringatan
- `--fastscan` tidak dapat digabung dengan `--threads`, `--timeout`, atau `--status`

---

## 💡 Contoh Penggunaan

```bash
# Scan semua path utama dengan konfigurasi cepat
python3 dreconisr.py -u https://testphp.vulnweb.com --fullscope --fastscan

# Simpan hasil scan admin ke file txt & json
python3 dreconisr.py -u https://juice-shop.herokuapp.com --admin --save --json

# Scan dengan delay 0.5 detik
python3 dreconisr.py -u https://example.com --fpath --delay 0.5

# Tampilkan semua status termasuk error
python3 dreconisr.py -u https://testphp.vulnweb.com --fullscope --verbose
```

---

## 🛠 Catatan Teknis

- Pada beberapa target, hasil yang muncul bisa berbeda tergantung konfigurasi `--threads` dan `--delay`. Jika respons terasa terbatas, mencoba dengan `--threads 1` kadang memberi hasil tambahan yang tidak terlihat dalam mode multithread.
- File hasil disimpan otomatis dengan timestamp

---

## 📍 Penutup

DreconisR dibuat untuk kebutuhan scanning cepat dan efisien, tanpa perlu instalasi tambahan. Bisa langsung digunakan di lingkungan terminal.

**Repo:** [https://github.com/G181124/DreconisR](https://github.com/G181124/DreconisR)