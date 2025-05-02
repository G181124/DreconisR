# DreconisR

DreconisR adalah alat pemindaian direktori berbasis CLI yang cepat, ringkas, dan fleksibel. Dirancang untuk memberikan hasil responsif dengan berbagai opsi pemfilteran dan preset kecepatan.

## Instalasi

```bash
https://github.com/G181124/DreconisR
cd DreconisR
pip install -r requirements.txt
```

## Penggunaan

```bash
python3 dreconisr.py -u https://target.com --auth-md --save
```

### Contoh Lain:

* Scan dengan wordlist kecil:

  ```bash
  python3 dreconisr.py -u https://target.com --fpath-sm
  ```

* Gunakan mode fastscan:

  ```bash
  python3 dreconisr.py -u https://target.com --fullscope --fastscan
  ```

* Gunakan mode ultrafast:

  ```bash
  python3 dreconisr.py -u https://target.com --auth-sm --ultrafast
  ```

* Simpan hasil dalam bentuk `.txt` dan `.drejson`:

  ```bash
  python3 dreconisr.py -u https://target.com --blur-sm --save --json
  ```

## Opsi Penting

| Flag           | Keterangan                                                 |
| -------------- | ---------------------------------------------------------- |
| `-u` / `--url` | Target URL yang akan dipindai                              |
| `--save`       | Menyimpan hasil ke folder `output/`                        |
| `--json`       | Menyimpan hasil juga dalam format JSON                     |
| `--status`     | Menampilkan hanya kode status tertentu (mis. `200,403`)    |
| `--timeout`    | Timeout request (default: 5 detik)                         |
| `--threads`    | Jumlah thread (default: 10, max: 100)                      |
| `--delay`      | Jeda antar request                                         |
| `--verbose`    | Tampilkan semua respons (termasuk 404, 500)                |
| `--fastscan`   | Preset cepat: threads=30, timeout=2, status=200,403        |
| `--ultrafast`  | Preset sangat cepat: threads=60, timeout=1, status=200,403 |

## Wordlist Flags

Gunakan hanya salah satu dari flag berikut untuk memilih wordlist:

* `--auth-sm`, `--auth-md`
* `--fpath`, `--fpath-sm`, `--fpath-md`, `--fpath-v`, `--fpath-rl`
* `--blur-sm`, `--blur-md`, `--blur-v`
* `--file-sm`, `--file-md`, `--file-v`
* `--extdoor`, `--vaultsight`, `--xmlgate`
* `--netdebug`, `--dbconsole`, `--oraframe`, `--sapsight`, `--springmap`
* `--core-asp`, `--core-php`, `--core-jsp`, `--core-pl`
* `--consulpeek`, `--formtags`, `--finderhole`, `--conflux`, `--goprobe`, `--nodemap`, `--rubytrace`, `--idflow`, `--vpnnode`
* `--fullscope`, `--fmanager`

## Catatan Tambahan

* Kecepatan pemindaian juga dipengaruhi oleh waktu respons dari target, bukan hanya pengaturan lokal Anda.
* Idealnya gunakan `--threads` dalam rentang 10–30 jika tidak menggunakan preset.
* Gunakan `--fastscan` atau `--ultrafast` **tanpa kombinasi pengaturan manual seperti `--timeout`, `--threads`, atau `--status`**.
