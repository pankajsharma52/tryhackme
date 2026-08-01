Day 4 | Easy • Network Forensics • PCAP Analysis

Opened the provided PCAP in Wireshark and analyzed the network traffic using the filters tcp.port == 8080, http.request, and http.cookie. The initial HTTP request downloaded /temp/updates.py, and inspecting the HTTP 200 OK response revealed the Python-based keylogger.

The keylogger contained the C2 URL (http://byte-lotus-hotel.thm:8080/), the XOR encryption key (H0t3lSt@ff0NlyK3epS3cr3t!), and showed that every captured keystroke was first UTF-8 encoded, then XOR encrypted, Base64 encoded, and finally exfiltrated to the C2 server inside the hotel_sess_state Cookie header using repeated HTTP GET requests.

After identifying the exfiltration method, extracted all hotel_sess_state Cookie values from the HTTP requests. Each Cookie value was Base64 decoded to recover the encrypted byte, then XOR decrypted using the key recovered from the keylogger to obtain the original keystroke. Finally, reassembled the decrypted characters in transmission order, reconstructing the victim's keystrokes and recovering the flag.
