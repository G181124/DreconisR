# File: dreconisr.py

import argparse
import os
import sys
import json
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# =========================
# Terminal Colors
# =========================
RED = "\033[91m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
GRAY = "\033[90m"
RESET = "\033[0m"

# =========================
# Banner
# =========================
def show_banner():
    banner = f"""
{CYAN} _____                             _      ______  
(____ \\                           (_)    (_____ \\ 
 _   \\ \\ ____ ____ ____ ___  ____  _  ___ _____) )
| |   | / ___) _  ) ___) _ \\|  _ \\| |/___|_____ ( 
| |__/ / |  ( (/ ( (__| |_| | | | | |___ |     | |
|_____/|_|   \\____)____)___/|_| |_|_(___/      |_|{RESET}
                                                  
{GREEN}[@] Author : RL
[~] Version : 1.0.0{RESET}
"""
    print(banner)

# =========================
# Argument Parser
# =========================
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="DreconisR - Fast Directory Scanner with clean CLI",
        epilog="Example: python3 dreconisr.py -u https://example.com --admin"
    )
    parser.add_argument("-u", "--url", required=True, help="Target URL (e.g., https://example.com)")
    parser.add_argument("--save", action="store_true", help="Save output result to /output/ folder")
    parser.add_argument("--json", action="store_true", help="Also save result as JSON format")
    parser.add_argument("--status", help="Only show specific status codes (e.g., 200,403)")
    parser.add_argument("--timeout", type=int, default=5, help="Request timeout in seconds (default: 5)")
    parser.add_argument("--threads", type=int, default=10, help="Number of threads to use (default: 10)")
    parser.add_argument("--verbose", action="store_true", help="Show all responses including 404 and 500")
    parser.add_argument("--fastscan", action="store_true", help="Use optimized config: threads=30, timeout=2, status=200,403")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--fullscope", action="store_true", help="Use fullscope wordlist (all-in-one)")
    group.add_argument("--admin", action="store_true", help="Scan with admin wordlist only")
    group.add_argument("--fpath", action="store_true", help="Scan with full path wordlist only")
    group.add_argument("--fmanager", action="store_true", help="Scan with file manager wordlist only")
    return parser.parse_args()

# =========================
# Wordlist Loader
# =========================
def load_wordlist(path):
    try:
        with open(path, 'r') as f:
            return [line.strip() for line in f if line.strip() != ""]
    except Exception as e:
        print(f"[!] Failed to load wordlist: {e}")
        sys.exit(1)

# =========================
# Status Code Filter
# =========================
def parse_status_filter(status_str):
    if not status_str:
        return None
    try:
        return set(int(code.strip()) for code in status_str.split(",") if code.strip().isdigit())
    except:
        print("[!] Invalid format for --status. Use comma-separated numbers (e.g., 200,403)")
        sys.exit(1)

# =========================
# Scanner Worker
# =========================
def scan_single_path(base_url, path, timeout, status_filter, verbose):
    full_url = base_url.rstrip("/") + "/" + path
    try:
        r = requests.get(full_url, timeout=timeout)
        code = r.status_code
        color = RESET
        tag = "[+]"

        if code == 200:
            color = GREEN
        elif code in [301, 302]:
            color = BLUE
        elif code == 403:
            color = YELLOW
        elif code == 404:
            color = GRAY
            tag = "[-]"
        elif code >= 500:
            color = RED
            tag = "[-]"
        else:
            color = RESET
            tag = "[-]"

        show = False
        if verbose:
            show = True
        elif status_filter:
            if code in status_filter:
                show = True
        else:
            if code in [200, 301, 302, 403]:
                show = True

        if show:
            print(f"{color}{tag} {code} => {full_url}{RESET}")
            return {"status": code, "url": full_url}
    except requests.exceptions.RequestException:
        return None

# =========================
# Scanner Main
# =========================
def scan_directory(url, wordlist, timeout, status_filter, threads, verbose):
    found = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(scan_single_path, url, path, timeout, status_filter, verbose) for path in wordlist]
        for future in futures:
            result = future.result()
            if result:
                found.append(result)
    return found

# =========================
# Output Saver
# =========================
def save_output(data, as_json=False):
    if not os.path.exists("output"):
        os.makedirs("output")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_txt = f"output/result_{timestamp}.txt"
    filename_json = f"output/result_{timestamp}.json"

    with open(filename_txt, 'w') as f:
        for entry in data:
            f.write(f"{entry['status']} => {entry['url']}\n")
    print(f"\n[+] Output saved to {filename_txt}")

    if as_json:
        with open(filename_json, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"[+] JSON output saved to {filename_json}")

# =========================
# Main Function
# =========================
def main():
    show_banner()
    args = parse_arguments()

    # Fastscan preset logic
    if args.fastscan:
        if args.threads != 10 or args.timeout != 5 or args.status:
            print("[!] Do not combine --fastscan with manual config (--threads, --timeout, --status).")
            sys.exit(1)
        args.threads = 30
        args.timeout = 2
        args.status = "200,403"
        print("[+] Fastscan mode activated: threads=30, timeout=2, status=200,403")

    # Validate threads
    if args.threads > 100:
        print("[!] Thread count too high. Max allowed: 100.")
        sys.exit(1)
    elif args.threads >= 50:
        print("[!] Warning: Thread count over 50 may overload weak networks, cause dropped packets, or trigger rate-limiting on the target server. Ideal range is 10–30.")
    elif args.threads < 1:
        print("[!] Thread count must be at least 1.")
        sys.exit(1)

    # Validate timeout
    if args.timeout > 60:
        print("[!] Timeout too high. Max allowed: 60 seconds. Excessive timeout may cause prolonged scan durations and unresponsiveness.")
        sys.exit(1)
    elif args.timeout > 10:
        print("[!] Warning: Timeout above 10 seconds is rarely needed. Ideal range is 2–5. Excessive wait may slow down overall performance.")
    elif args.timeout < 1:
        print("[!] Timeout must be at least 1 second.")
        sys.exit(1)

    if args.fullscope:
        wordlist_path = "xdata/fullscope.txt"
    elif args.admin:
        wordlist_path = "xdata/authpaths.txt"
    elif args.fpath:
        wordlist_path = "xdata/deepmap.txt"
    elif args.fmanager:
        wordlist_path = "xdata/uplinks.txt"
    else:
        wordlist_path = "xdata/deepmap.txt"  # default fallback

    print(f"[{datetime.now().strftime('%Y-%m-%d')}] [{datetime.now().strftime('%H:%M:%S')}] Parsing Wordlist...")
    wordlist = load_wordlist(wordlist_path)
    print(f"[{datetime.now().strftime('%Y-%m-%d')}] [{datetime.now().strftime('%H:%M:%S')}] Wordlist is Ready")
    print(f"[{datetime.now().strftime('%Y-%m-%d')}] [{datetime.now().strftime('%H:%M:%S')}] Total Paths to Check: {len(wordlist)}")

    status_filter = parse_status_filter(args.status)

    print(f"[{datetime.now().strftime('%Y-%m-%d')}] [{datetime.now().strftime('%H:%M:%S')}] Checking HOST...")
    print(f"[{datetime.now().strftime('%Y-%m-%d')}] [{datetime.now().strftime('%H:%M:%S')}] {args.url} Is Ready\n")

    results = scan_directory(args.url, wordlist, args.timeout, status_filter, args.threads, args.verbose)

    if args.save:
        save_output(results, as_json=args.json)

if __name__ == "__main__":
    main()
