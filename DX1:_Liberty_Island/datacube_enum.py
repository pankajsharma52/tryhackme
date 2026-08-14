import requests
# Replace the IP address below with the target machine's IP.
target = "http://10.48.146.209/datacubes/"

for i in range(1001):
    path = f"{i:04d}/"

    try:
        r = requests.get(target + path, timeout=5)

        if r.status_code == 200 and r.text.strip():
            print(f"\n[+] {path}")
            print(r.text)

    except requests.RequestException:
        pass
