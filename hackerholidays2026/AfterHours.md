# After Hours

**Difficulty:** Medium
**Category:** Forensics · Windows Persistence · Reverse Engineering

## Summary

The challenge involved investigating a Windows persistence mechanism that was not detected by common persistence locations such as Startup, Scheduled Tasks, or Registry Run keys.

The provided files were a Windows WMI Repository:

```text
OBJECTS.DATA
INDEX.BTR
MAPPING1.MAP
MAPPING2.MAP
MAPPING3.MAP
```

The investigation revealed a WMI-based PowerShell persistence mechanism that retrieved a compressed .NET assembly from WMI. The assembly was then analyzed with ILSpy to recover the flag.

## Attack Chain

```text
WMI Repository
    ↓
OBJECTS.DATA
    ↓
PowerShell persistence
    ↓
Base64-encoded PowerShell
    ↓
Win32_HardwareTelemetry
    ↓
ConfigData
    ↓
Base64
    ↓
Raw Inflate
    ↓
.NET Assembly
    ↓
ILSpy
    ↓
Base64
    ↓
Flag
```

## Enumeration

The `OBJECTS.DATA` file was converted into readable strings:

```bash
strings OBJECTS.DATA > objects.txt
```

The extracted strings were searched for WMI persistence-related keywords:

```bash
grep -Ei "EventFilter|Consumer|Binding|PowerShell|CommandLine" objects.txt
```

A more targeted PowerShell search was then performed:

```bash
grep -i powershell objects.txt
```

This revealed:

```text
cmd /C powershell.exe -Sta -Nop -Window Hidden -enc <Base64>
```

The `-enc` parameter indicated that the PowerShell command was Base64 encoded.

## PowerShell Payload

After decoding the Base64 value, the following PowerShell logic was obtained:

```powershell
$file = ([WmiClass]'ROOT\cimv2:Win32_HardwareTelemetry').Properties['ConfigData'].Value;
$o = New-Object IO.MemoryStream;
$d = New-Object IO.Compression.DeflateStream(
    [IO.MemoryStream][Convert]::FromBase64String($file),
    [IO.Compression.CompressionMode]::Decompress
);
```

The script retrieves the `ConfigData` property from:

```text
ROOT\cimv2:Win32_HardwareTelemetry
```

The retrieved value was then Base64 decoded and decompressed.

## Extracting ConfigData

The WMI class was located in the extracted strings:

```bash
grep -C 3 'Win32_HardwareTelemetry' objects.txt
```

This revealed a large Base64-encoded payload.

The payload was processed in **CyberChef** using:

```text
From Base64
↓
Raw Inflate
```

The resulting data was saved as a file.

The decoded script also showed that the resulting bytes were loaded as a .NET assembly:

```powershell
[Reflection.Assembly]::Load($o.ToArray())
```

## Reverse Engineering

The extracted .NET assembly was opened in **ILSpy**.

Inside the `Main()` method, another Base64-encoded string was found.

Decoding that final Base64 string revealed the flag.

## Flag

```text
`THM{P4tch_******_***_********}`
```
