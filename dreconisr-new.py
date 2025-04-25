import argparse
import os
import sys
import json
import requests
import time
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
[~] Version : 1.0.0{RESET}"""
    print(banner)

# =========================
# Load Wordlist JSON Config [GR]
# =========================
with open(os.path.join(os.path.dirname(__file__), "dreconisr_lists.json"), "r") as f:  # [GR]
    wordlist_config = json.load(f)  # [GR]

WORDLIST_MAP = {k: v["path"] for k, v in wordlist_config.items()}  # [GR]
HELP_MAP = {k: v["desc"] for k, v in wordlist_config.items()}  # [GR]

# =========================
# Argument Parser
# =========================
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="DreconisR - Fast Directory Scanner with clean CLI",
        epilog=(
            "Example Usage:\n"
            "  python3 dreconisr.py -u https://example.com --admin --save\n"
            "  python3 dreconisr.py -u https://target.com --fullscope --fastscan\n\n"
            "Notes:\n"
            "  --threads: Ideal range 10–30. Max 100. Too high can trigger rate-limits.\n"
            "  --timeout: Ideal 2–5 sec. Max 60. Timeout >10 may slow scanning.\n"
            "  --fastscan: Use optimal preset (threads=30, timeout=2, status=200,403).\n"
            "  --delay: Add delay between requests (in seconds). Useful to avoid bans."
        )
    )
    parser.add_argument("-u", "--url", required=True, help="Target URL (e.g., https://example.com)")
    parser.add_argument("--save", action="store_true", help="Save output result to /output/ folder")
    parser.add_argument("--json", action="store_true", help="Also save result as JSON format")
    parser.add_argument("--status", help="Only show specific status codes (e.g., 200,403)")
    parser.add_argument("--timeout", type=int, default=5, help="Request timeout in seconds (default: 5)")
    parser.add_argument("--threads", type=int, default=10, help="Number of threads to use (default: 10)")
    parser.add_argument("--delay", type=float, default=0, help="Delay (in seconds) between each request (default: 0)")
    parser.add_argument("--verbose", action="store_true", help="Show all responses including 404 and 500")
    parser.add_argument("--fastscan", action="store_true", help="Use optimized config: threads=30, timeout=2, status=200,403")

    group = parser.add_mutually_exclusive_group()
    for key in WORDLIST_MAP:
        group.add_argument(f"--{key}", action="store_true", help=HELP_MAP.get(key, f"Use wordlist: {WORDLIST_MAP[key]}"))

    return parser.parse_args()

# =========================
# Wordlist Loader
# =========================
def load_wordlist(path):
    try:
        with open(path, 'r') as f:
            return list(dict.fromkeys([line.strip() for line in f if line.strip() != ""]))
    except Exception as e:
        print(f"{RED}[!] Failed to load wordlist: {e}{RESET}")
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
        print(f"{RED}[!] Invalid format for --status. Use comma-separated numbers (e.g., 200,403){RESET}")
        sys.exit(1)

# =========================
# Scanner Worker
# =========================
def scan_single_path(base_url, path, timeout, status_filter, verbose, delay):
    full_url = base_url.rstrip("/") + "/" + path
    try:
        r = requests.get(full_url, timeout=timeout)
        time.sleep(delay)
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
def scan_directory(url, wordlist, timeout, status_filter, threads, verbose, delay):
    found = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(scan_single_path, url, path, timeout, status_filter, verbose, delay) for path in wordlist]
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
    filename_json = f"output/result_{timestamp}.drejson"

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

    if args.fastscan:
        if args.threads != 10 or args.timeout != 5 or args.status:
            print(f"{RED}[!] Do not combine --fastscan with manual config (--threads, --timeout, --status).{RESET}")
            sys.exit(1)
        args.threads = 30
        args.timeout = 2
        args.status = "200,403"
        print(f"{GREEN}[+] Fastscan mode activated: threads=30, timeout=2, status=200,403{RESET}")

    if args.threads > 100:
        print(f"{RED}[!] Thread count too high. Max allowed: 100.{RESET}")
        sys.exit(1)
    elif args.threads >= 50:
        print(f"{YELLOW}[!] Warning: Thread count over 50 may overload weak networks, cause dropped packets, or trigger rate-limiting on the target server. Ideal range is 10–30.{RESET}")
    elif args.threads < 1:
        print(f"{RED}[!] Thread count must be at least 1.{RESET}")
        sys.exit(1)

    if args.timeout > 60:
        print(f"{RED}[!] Timeout too high. Max allowed: 60 seconds. Excessive timeout may cause prolonged scan durations and unresponsiveness.{RESET}")
        sys.exit(1)
    elif args.timeout > 10:
        print(f"{YELLOW}[!] Warning: Timeout above 10 seconds is rarely needed. Ideal range is 2–5. Excessive wait may slow down overall performance.{RESET}")
    elif args.timeout < 1:
        print(f"{RED}[!] Timeout must be at least 1 second.{RESET}")
        sys.exit(1)

    # Determine selected wordlist [GR]
    selected_wordlist = None
    for flag, path in WORDLIST_MAP.items():
        if getattr(args, flag.replace("-", "_"), False):
            selected_wordlist = path
            break
    if not selected_wordlist:
        selected_wordlist = WORDLIST_MAP["fpath"]  # fallback default

    print(f"[{datetime.now().strftime('%Y-%m-%d')}] [{datetime.now().strftime('%H:%M:%S')}] Parsing Wordlist...")
    wordlist = load_wordlist(selected_wordlist)
    print(f"[{datetime.now().strftime('%Y-%m-%d')}] [{datetime.now().strftime('%H:%M:%S')}] Wordlist is Ready")
    print(f"[{datetime.now().strftime('%Y-%m-%d')}] [{datetime.now().strftime('%H:%M:%S')}] Total Paths to Check: {len(wordlist)}")

    status_filter = parse_status_filter(args.status)

    print(f"[{datetime.now().strftime('%Y-%m-%d')}] [{datetime.now().strftime('%H:%M:%S')}] Checking HOST...")
    print(f"[{datetime.now().strftime('%Y-%m-%d')}] [{datetime.now().strftime('%H:%M:%S')}] {args.url} Is Ready\n")

    results = scan_directory(args.url, wordlist, args.timeout, status_filter, args.threads, args.verbose, args.delay)

    if args.save:
        save_output(results, as_json=args.json)

if __name__ == "__main__":
    main()
