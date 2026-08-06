# The Hollow Shell

**Difficulty:** Medium  
**Category:** Web Security, File Upload, Zip Slip

---

## Summary

The Hollow Shell is a web-based challenge focused on authenticated file upload vulnerabilities. During enumeration, hardcoded credentials were discovered in the application's page source, providing access to the authenticated dashboard. The application accepted ZIP-based shell packages, and further testing revealed a **Zip Slip (Path Traversal)** vulnerability that could be abused to write files outside the intended extraction directory. By leveraging the application's automated theme worker, code execution was achieved, allowing retrieval of the user flag.

---

# Attack Chain

1. Inspect the application's page source.
2. Discover hardcoded login credentials.
3. Authenticate to the dashboard.
4. Analyze the ZIP upload functionality.
5. Identify the Zip Slip vulnerability.
6. Abuse directory traversal during archive extraction.
7. Write a file into the application's hook directory.
8. Trigger the theme worker.
9. Gain code execution as the `roomservice` user.
10. Retrieve the flag.

---

# Enumeration

## Port Scan

The target exposed the following services:

| Port | Service |
|------|---------|
| 22 | SSH |
| 5000 | Web Application |

The web application running on **port 5000** was the primary attack surface.

---

## Authenticated Dashboard

Using the credentials discovered in the page source, access was obtained to the dashboard.

The application allowed users to upload ZIP archives containing a required `shell.json` manifest along with supported assets. The interface also mentioned **automation hooks**, indicating that uploaded themes were processed automatically by a background worker.

---

# Zip Slip Exploitation

A valid ZIP archive containing `shell.json` was created to understand the expected upload structure. Further testing showed that archive entries containing traversal sequences (`../`) were extracted outside the intended upload directory, confirming a **Zip Slip (Path Traversal)** vulnerability.

The application's automated processing mechanism referenced **hooks**, making it possible to place a crafted file inside the hook directory. When processed by the background worker (`theme_worker.py`), code execution was achieved as the **roomservice** user.

After gaining execution, the following application structure was identified:

```text
/var/www/conch

├── app.py
├── hooks/
├── requirements.txt
├── shells/
├── static/
├── templates/
├── theme_worker.py
├── venv/
└── __pycache__/
```

The user flag was located at:

```text
/home/roomservice/flag.txt
```

---

# Mitigation

- Never expose credentials within client-side source code.
- Validate ZIP archive entries before extraction.
- Reject archive entries containing directory traversal sequences (`../`).
- Normalize extraction paths and ensure all extracted files remain within the intended upload directory.
