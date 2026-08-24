# Daily Bugle

**Difficulty:** Hard
**Category:** Web Exploitation / Privilege Escalation

## Summary

Daily Bugle is a Linux machine running a Joomla CMS. The attack involved exploiting a Joomla SQL Injection vulnerability to extract administrator credentials, cracking the password hash, and using the obtained credentials to access the Joomla administrator panel. A PHP reverse shell was then deployed through the template editor to gain an `apache` shell.

After enumerating the system, credentials for `jjameson` were discovered in a PHP configuration file. Finally, `yum` was abused through a sudo misconfiguration to obtain a root shell.

## Attack Chain

Joomla SQLi → Credential Extraction → Hash Cracking → Joomla Admin Access → Template RCE → `apache` → `jjameson` → `yum` Sudo Abuse → `root`

## Enumeration

Nmap revealed the following relevant services:

* `22` — SSH
* `80` — HTTP
* `3306` — MySQL

Web enumeration identified the target as a Joomla installation with an exposed administrator panel.

Further enumeration revealed that the installed Joomla version was affected by a known SQL Injection vulnerability, **CVE-2017-8917**.

## Initial Access

The attached Python exploit script was used to exploit the Joomla SQL Injection vulnerability.

```bash
python3 exploit.py http://TARGET
```


The script enumerated the Joomla database and extracted user information, including the administrator username and password hash.

The extracted bcrypt hash was cracked using John the Ripper:

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

The recovered credentials were then used to authenticate to the Joomla administrator panel.

### Joomla Template RCE

After obtaining administrator access, the template editor was used to modify the template's `index.php`.

A PHP reverse-shell payload was inserted and the **Template Preview** functionality was used to trigger it.

A listener was started on the attacking machine:

```bash
nc -lvnp 4444
```

This resulted in a reverse shell as:

```text
apache
```

## User Access

The `apache` shell was used to enumerate the filesystem and identify the `jjameson` user.

The target's /tmp directory was writable, so LinPEAS was transferred there from the attacking machine, given execute permission, and executed for further enumeration.

During enumeration, credentials were discovered in PHP configuration files. The recovered password was reused for the `jjameson` account.

After switching to `jjameson`, the user flag was obtained from:

```text
/home/jjameson/user.txt
```

## Privilege Escalation

The sudo permissions for `jjameson` were checked:

```bash
sudo -l
```

The important permission was:

```text
(ALL) NOPASSWD: /usr/bin/yum
```

This allowed `yum` to be executed as root without authentication.

A malicious yum plugin was created in a temporary directory and loaded through a custom yum configuration. The plugin executed `/bin/sh`, resulting in a root shell.

```bash
TF=$(mktemp -d)

cat >"$TF/x" <<EOF
[main]
plugins=1
pluginpath=$TF
pluginconfpath=$TF
EOF

cat >"$TF/yum-plugin.conf" <<'EOF'
[main]
enabled=1
EOF

cat >"$TF/yum-plugin.py" <<'EOF'
import os
os.execl("/bin/sh", "sh")
EOF

sudo /usr/bin/yum -c "$TF/x"
```

The resulting shell had root privileges.

The root flag was then retrieved from:

```text
/root/root.txt
```

## Mitigation

* Upgrade Joomla to a supported and patched release.
* Remove unnecessary `NOPASSWD` sudo permissions for command-line utilities such as `yum`.
