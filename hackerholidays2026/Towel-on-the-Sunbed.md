# Towel on the Sunbed

**Difficulty:** Medium
**Category:** Web Exploitation, Business Logic, API Abuse

## Summary

This room focuses on exploiting a race condition in a daily reward system. By abusing the reward claim mechanism with concurrent requests, it is possible to bypass the intended cooldown, increase the account balance to the required threshold, and access the Whale Vault to obtain the flag.

---

## Attack Chain

1. Register a new account and log in.
2. Explore the dashboard and identify the reward claim functionality.
3. Intercept the `POST /claim` request using Burp Suite.
4. Send the request to **Repeater** and create a request group.
5. Execute the grouped requests **in parallel** to trigger a race condition.
6. Receive multiple reward credits before the cooldown is applied.
7. Reach the required balance of **150 PONZI**.
8. Access the `/vault` endpoint and retrieve the flag.

---

## Enumeration

* Registered a guest account and explored the application.
* Identified the following endpoints:

  * `POST /claim`
  * `GET /dashboard/api/me`
* Verified that the Whale Vault requires a minimum balance of **150 PONZI**.

---

## Initial Access

The daily reward feature was vulnerable to a race condition. The `POST /claim` request was intercepted with Burp Suite and sent to Repeater. By creating a request group and executing the requests simultaneously, multiple reward claims were processed before the server updated the cooldown state. This allowed the account balance to exceed the Whale Vault requirement, making the `/vault` endpoint accessible and revealing the flag.

---

## Mitigation

* Process reward claims using atomic database transactions.
* Lock user records while processing reward requests.
* Update the reward cooldown and user balance atomically.
* Prevent multiple concurrent reward claims for the same account.
