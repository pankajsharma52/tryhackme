# Prioritise

**Difficulty:** Medium
**Category:** SQL Injection 

---
## Enumeration

The room hint states:

> In this challenge you will explore some less common SQL Injection techniques.

After exploring the web application and testing the available parameters, the `order=` parameter was identified as the injection point.

The vulnerable request was captured using *Burp Suite* and saved as `sql.txt`.

## Exploitation

The captured request was passed to SQLMap using:

```bash
sqlmap -r sql.txt --dump --level=2 --risk=2
```
SQLMap successfully exploited the SQL Injection vulnerability and dumped the database contents. The flag was obtained from the dumped data
